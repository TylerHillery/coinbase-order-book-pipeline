import pandas as pd
import psycopg2
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

# database connection
dsn = "user=materialize password=password host=localhost port=6875 dbname=materialize"
conn = psycopg2.connect(dsn)
cur = conn.cursor()

# Streamlit configs
st.set_page_config(
    layout="wide",
    page_title="Coinbase Level 2 Channel",
)

precision = {
    "BTC-USD": 2,
    "ETH-USD": 2,
    "DOGE-USD": 6
}
with st.sidebar:
    selected_market = st.selectbox("Select Market",precision.keys())
    refresh_interval = st.slider('Auto-Refresh Interval (seconds)', 1, 15, step=1)
    bps_offset = st.slider(
        'Select offset from NBBO (bps)', 
        10, 
        1000, 
        step=10, 
        help="Basis point:\n One hundredth of one percent e.g. 1% = 100bps"
    ) / 10_000

st_autorefresh(interval=refresh_interval*1000)

sql_query = '''
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
'''
cur.execute(sql_query,(selected_market,))

nbb_price, nbb_size, nbo_price, nbo_size, nbbo_midpoint, nbbo_spread = cur.fetchone()

st.markdown(f"<h1 style='text-align: center;'>Coinbase {selected_market} Level 2 Channel</h1>", unsafe_allow_html=True)

with st.container():
    c2,c3,c4 = st.columns([3,3,3])
    c2.markdown(f"""
    <div style="text-align: center;">
        <span style="font-size: 12px; color: #888888;"><strong>BEST BID</strong></span>
        <br> 
        <span style="font-size: 36px;"><strong>${nbb_price:,.{precision[selected_market]}f}</strong></span>
        <br>
        x {nbb_size:,}
    </div>
        """, 
        unsafe_allow_html=True,
    )

    c3.markdown(f"""
    <div style="text-align: center;">         
        <span style="font-size: 12px; color: #888888;"><strong>MID MARKET PRICE</strong></span>
        <br> 
        <span style="font-size: 36px;"><strong>${nbbo_midpoint:,.{precision[selected_market]}f}</strong></span>
    </div>
        """, 
        unsafe_allow_html=True,
    )

    c4.markdown(f"""
    <div style="text-align: center;">  
        <span style="font-size: 12px; color: #888888;"><strong>BEST ASK</strong></span>
        <br>
        <span style="font-size: 36px;"><strong>${nbo_price:,.{precision[selected_market]}f}</strong></span>
        <br>
        x {nbo_size:,}
    </div>
    """, 
    unsafe_allow_html=True,
    )


sql_query = '''
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
;'''

cur.execute(sql_query,(selected_market,bps_offset,bps_offset))
column_headers = [
    "Market", 
    "Side", 
    "Price", 
    "Size",
]
leve2_channel_df = pd.DataFrame(cur.fetchall(), columns=column_headers)
conn.close()

buy_df = leve2_channel_df[leve2_channel_df["Side"] == "buy"].sort_values(by="Price", ascending=False)
sell_df = leve2_channel_df[leve2_channel_df["Side"] == "sell"].sort_values(by="Price", ascending=True)

buy_df["Cumulative Size"] = buy_df["Size"].cumsum()
sell_df["Cumulative Size"] = sell_df["Size"].cumsum()

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=buy_df["Price"],
    y=buy_df["Cumulative Size"],
    fill='tozeroy',
    mode='lines', 
    line=dict(color='cyan'),
    name='Bids'
))
fig.add_trace(go.Scatter(
    x=sell_df["Price"],
    y=sell_df["Cumulative Size"],
    fill='tozeroy',
    mode='lines', 
    line=dict(color='purple'),    
    name='Asks'        
))
fig.update_xaxes(tickformat='$,')
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.0,
    xanchor="right",
    x=1
))
st.plotly_chart(fig, x="Price", y="Size", color="Side", use_container_width=True)

def color_cyan(val):
    return 'color: cyan'

def color_purple(val):
    return 'color: #d718e3'

buy_columns = ["Size","Price"]
sell_columns = ["Price","Size"]
with st.container():
    c0,c1,c2 = st.columns([.2,5,5])

    buy_df_html = (
        buy_df[buy_columns].head(10)
            .style
            .applymap(color_cyan, subset=["Price"])
            .format({
                "Price": lambda x: f"${x:,.{precision[selected_market]}f}"
            })
            .bar(subset=["Size"], color='#07888b')
            .hide(axis="index")
            .set_properties(subset=['Size'], **{'width': '300px'})
            .set_properties(subset=['Price'], **{'width': '200px'})
            .set_table_styles([
                {
                    'selector': 'caption',
                    'props': [
                        ('caption-side', 'top'),
                        ('text-align', 'center')
                    ]
                },
                {
                    'selector': 'th', 
                    'props': [
                        ('text-align', 'center'),
                        ('border', 'none'),
                    ]
                },
                {
                    'selector': 'td', 
                    'props': [
                        ('text-align', 'center'),
                    ]
                }
            ])
            .set_caption("Bids")
            .to_html(escape=False)
    ).replace("<table ", '<table align="right"')

    c1.write(buy_df_html,unsafe_allow_html=True)
    
    sell_df_html = (
        sell_df[sell_columns].head(10)
        .style
        .applymap(color_purple, subset=["Price"])
        .format({
            "Price": lambda x: f"${x:,.{precision[selected_market]}f}"
        })
        .bar(subset=["Size"], color='#47084b')
        .hide(axis="index")
        .set_properties(subset=['Size'], **{'width': '300px'})
        .set_properties(subset=['Price'], **{'width': '200px'})
        .set_table_styles([
                {
                    'selector': 'caption',
                    'props': [
                        ('caption-side', 'top'),
                        ('text-align', 'center')
                    ]
                },
                {
                    'selector': 'th', 
                    'props': [
                        ('text-align', 'center'),
                        ('border', 'none'),
                    ]
                },
                {
                    'selector': 'td', 
                    'props': [
                        ('text-align', 'center'),
                    ]
                }
            ])
        .set_caption("Asks")
        .to_html(escape=False)
    ).replace("<table",'<table align="left"')

    c2.write(sell_df_html,unsafe_allow_html=True)