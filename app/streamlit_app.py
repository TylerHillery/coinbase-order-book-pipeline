import psycopg2
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

import utils

# Config stuff
st.set_page_config(
    layout="wide",
    page_title="Coinbase Level 2 Channel",
)

dsn = "user=materialize password=password host=materialized port=6875 dbname=materialize"
conn = psycopg2.connect(dsn)
cur = conn.cursor()

PRECISION = {
    "BTC-USD": 2,
    "ETH-USD": 2,
    "DOGE-USD": 6
}

# Sidebar
with st.sidebar:
    selected_market = st.selectbox("Select Market",PRECISION.keys())
    refresh_interval = st.slider(
        "Auto-Refresh Interval (seconds)", 
        1, 
        15, 
        step=1
    )
    bps_offset = st.slider(
        "Select offset from NBBO (bps)", 
        10, 
        1000, 
        step=10, 
        help="Basis point:\n One hundredth of one percent e.g. 1% = 100bps"
    ) / 10_000

st_autorefresh(interval=refresh_interval*1000)

# Get Data
nbbo_data = utils.get_nbbo_data(cur,selected_market)
buy_df, sell_df = utils.get_level2_data(cur,selected_market,bps_offset)

conn.close()

# Title
st.markdown(f"""
    <h1 style='text-align: center;'>
        Coinbase {selected_market} Level 2 Channel
    </h1>
    """, 
    unsafe_allow_html=True
)

# Metrics
with st.container():
    c2,c3,c4 = st.columns([3,3,3])
    c2.markdown(f"""
    <div style="text-align: center;">
        <span style="font-size: 12px; color: #888888;">
            <strong>BEST BID</strong>
        </span>
        <br> 
        <span style="font-size: 36px;">
            <strong>${nbbo_data["nbb_price"]:,.{PRECISION[selected_market]}f}</strong>
        </span>
        <br>
        x {nbbo_data["nbb_size"]:,}
    </div>
        """, 
        unsafe_allow_html=True,
    )

    c3.markdown(f"""
    <div style="text-align: center;">         
        <span style="font-size: 12px; color: #888888;">
            <strong>MID MARKET PRICE</strong>
        </span>
        <br> 
        <span style="font-size: 36px;">
                <strong>${nbbo_data["nbbo_midpoint"]:,.{PRECISION[selected_market]}f}</strong>
        </span>
    </div>
        """, 
        unsafe_allow_html=True,
    )

    c4.markdown(f"""
    <div style="text-align: center;">  
        <span style="font-size: 12px; color: #888888;">
                <strong>BEST ASK</strong>
        </span>
        <br>
        <span style="font-size: 36px;">
                <strong>${nbbo_data["nbo_price"]:,.{PRECISION[selected_market]}f}</strong>
        </span>
        <br>
        x {nbbo_data["nbo_size"]:,}
    </div>
    """, 
    unsafe_allow_html=True,
    )

# Area Chart
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=buy_df["Price"],
    y=buy_df["Cumulative Size"],
    fill="tozeroy",
    mode="lines", 
    line=dict(color="cyan"),
    name="Bids"
))

fig.add_trace(go.Scatter(
    x=sell_df["Price"],
    y=sell_df["Cumulative Size"],
    fill="tozeroy",
    mode="lines", 
    line=dict(color="purple"),    
    name="Asks"        
))

fig.update_xaxes(tickformat="$,")

fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.0,
    xanchor="right",
    x=1
))
st.plotly_chart(fig, x="Price", y="Size", color="Side", use_container_width=True)

# Tables
with st.container():
    c0,c1,c2 = st.columns([.2,5,5])    
    buy_columns = ["Size","Price"]
    sell_columns = ["Price","Size"]

    c1.write(
        utils.get_df_html(buy_df,buy_columns,selected_market,PRECISION,"cyan","#07888b","Bids",10),
        unsafe_allow_html=True
    )

    c2.write(
        utils.get_df_html(sell_df,sell_columns,selected_market,PRECISION,"#d718e3","#47084b","Asks",10),
        unsafe_allow_html=True
    )