import streamlit as st
import requests

st.title("Conexión a Alpaca (Paper)")

API_KEY = st.secrets["ALPACA_API_KEY"]
SECRET_KEY = st.secrets["ALPACA_SECRET_KEY"]

url = "https://paper-api.alpaca.markets/v2/account"

headers = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    st.success("Conectado correctamente a Alpaca 🎉")
    st.write(response.json())
else:
    st.error("Error al conectar")
    st.write(response.status_code)
    st.write(response.text)
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("Angel Trader PRO")

symbol = st.sidebar.text_input("Símbolo", "AAPL")
interval = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "1d"])

if interval in ["1m", "5m", "15m"]:
    period = "1d"
elif interval == "1h":
    period = "5d"
else:
    period = "1mo"

data = yf.download(tickers=symbol, period=period, interval=interval)

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close']
))

fig.update_layout(
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    height=700
)

st.plotly_chart(fig, use_container_width=True)
