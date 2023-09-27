import pandas as pd
import psycopg2

def get_nbbo_data(cur,selected_market):
    sql_query = """
    SELECT
        nbb_price,
        nbb_size,
        nbo_price,
        nbo_size,  
        nbbo_midpoint,
        nbbo_spread
    FROM
        fct_coinbase_nbbo
    WHERE
        product_id = %s
    """
    cur.execute(sql_query,(selected_market,))
    
    data = cur.fetchone()

    results = {
        "nbb_price":        data[0],
        "nbb_size":         data[1], 
        "nbo_price":        data[2], 
        "nbo_size":         data[3], 
        "nbbo_midpoint":    data[4], 
        "nbbo_spread":      data[5],
    }

    return results

def get_level2_data(cur, selected_market, bps_offset):
    sql_query = """
    WITH
    level2 AS (
        SELECT
            product_id,
            side,
            price,
            size
        FROM
            stg_coinbase_level2_channel
        WHERE 
            product_id = %s
    ),
    level2_bids AS (
        SELECT
            level2.product_id,
            level2.side,
            level2.price,
            level2.size
        FROM
            level2
            INNER JOIN fct_coinbase_nbbo
                ON level2.product_id = fct_coinbase_nbbo.product_id
                AND level2.side = 'buy'
                AND level2.price < fct_coinbase_nbbo.nbb_price
                AND level2.price >= fct_coinbase_nbbo.nbb_price * (1.0000 - %s)
    ),
    level2_asks AS (
        SELECT
            level2.product_id,
            level2.side,
            level2.price,
            level2.size
        FROM
            level2
            INNER JOIN fct_coinbase_nbbo
                ON level2.product_id = fct_coinbase_nbbo.product_id
                AND level2.side = 'sell'
                AND level2.price <= fct_coinbase_nbbo.nbb_price * (1.0000 + %s)
                AND level2.price > fct_coinbase_nbbo.nbo_price
    ),
    unioned AS (
        SELECT * FROM level2_bids
        UNION ALL
        SELECT * FROM level2_asks
    )
    SELECT 
        product_id,
        side,
        price,
        size
    FROM 
        unioned
    ;"""

    cur.execute(sql_query,(selected_market,bps_offset,bps_offset))
    
    column_headers = ["Market", "Side", "Price", "Size"]

    leve2_channel_df = pd.DataFrame(cur.fetchall(), columns=column_headers)

    buy_df = (leve2_channel_df[leve2_channel_df["Side"] == "buy"]
              .sort_values(by="Price", ascending=False)
            )
    sell_df = (leve2_channel_df[leve2_channel_df["Side"] == "sell"]
               .sort_values(by="Price", ascending=True)
            )
    
    buy_df["Cumulative Size"] = buy_df["Size"].cumsum()
    sell_df["Cumulative Size"] = sell_df["Size"].cumsum()

    return buy_df, sell_df


def get_df_html(df, columns, selected_market, precision, text_color, bar_color, caption, rows=10):
    df_html = (df[columns].head(rows)
                .style
                .applymap(lambda x: f"color: {text_color}", subset=["Price"])
                .format({
                "Price": lambda x: f"${x:,.{precision[selected_market]}f}"
                })
                .bar(subset=["Size"], color=bar_color)
                .hide(axis="index")
                .set_properties(subset=["Size"], **{"width": "300px"})
                .set_properties(subset=["Price"], **{"width": "200px"})
                .set_table_styles([
                    {
                        "selector": "caption",
                        "props": [
                            ("caption-side", "top"),
                            ("text-align", "center")
                        ]
                    },
                    {
                        "selector": "th", 
                        "props": [
                            ("text-align", "center"),
                            ("border", "none"),
                        ]
                    },
                    {
                        "selector": "td", 
                        "props": [
                            ("text-align", "center"),
                        ]
                    }
                ])
                .set_caption(caption)
                .to_html(escape=False)
        ).replace("<table ", "<table align='right'")
    
    return df_html