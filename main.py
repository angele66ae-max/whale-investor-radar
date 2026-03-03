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
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")
st.title("Angel Trader PRO 🔥")

# --- SIDEBAR ---
symbol = st.sidebar.text_input("Símbolo", "AAPL")
interval = st.sidebar.selectbox("Timeframe", ["5m", "15m", "1h", "1d"])

if interval in ["5m", "15m"]:
    period = "5d"
elif interval == "1h":
    period = "1mo"
else:
    period = "6mo"

# --- DESCARGA DATOS ---
data = yf.download(tickers=symbol, period=period, interval=interval)

# --- INDICADORES ---
data["EMA9"] = data["Close"].ewm(span=9).mean()
data["EMA21"] = data["Close"].ewm(span=21).mean()

delta = data["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss
data["RSI"] = 100 - (100 / (1 + rs))

# --- SEÑALES ---
data["Signal"] = 0
data.loc[data["EMA9"] > data["EMA21"], "Signal"] = 1
data.loc[data["EMA9"] < data["EMA21"], "Signal"] = -1

# --- CREAR SUBPLOTS ---
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    row_heights=[0.7, 0.3],
    vertical_spacing=0.05
)

# --- VELAS ---
fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"],
    name="Precio"
), row=1, col=1)

# --- EMAs ---
fig.add_trace(go.Scatter(
    x=data.index,
    y=data["EMA9"],
    line=dict(width=1),
    name="EMA 9"
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=data.index,
    y=data["EMA21"],
    line=dict(width=1),
    name="EMA 21"
), row=1, col=1)

# --- RSI ---
fig.add_trace(go.Scatter(
    x=data.index,
    y=data["RSI"],
    line=dict(width=1),
    name="RSI"
), row=2, col=1)

fig.add_hline(y=70, line_dash="dash", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", row=2, col=1)

# --- ESTILO ---
fig.update_layout(
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    height=800
)

st.plotly_chart(fig, use_container_width=True)

# --- SEÑAL ACTUAL ---
last_signal = data["Signal"].iloc[-1]

if last_signal == 1:
    st.success("🟢 Señal actual: COMPRA")
elif last_signal == -1:
    st.error("🔴 Señal actual: VENTA")
else:
    st.warning("⚪ Sin señal clara")
import requests
import json

st.markdown("---")
st.header("Trading en Vivo (Paper)")

API_KEY = st.secrets["ALPACA_API_KEY"]
SECRET_KEY = st.secrets["ALPACA_SECRET_KEY"]

BASE_URL = "https://paper-api.alpaca.markets"

headers = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY,
    "Content-Type": "application/json"
}

# --- Obtener cuenta ---
account = requests.get(f"{BASE_URL}/v2/account", headers=headers).json()

col1, col2, col3 = st.columns(3)

col1.metric("💰 Portfolio", f"${float(account['portfolio_value']):,.2f}")
col2.metric("💵 Cash", f"${float(account['cash']):,.2f}")
col3.metric("⚡ Buying Power", f"${float(account['buying_power']):,.2f}")

st.markdown("---")

qty = st.number_input("Cantidad de acciones", min_value=1, value=1)

col_buy, col_sell = st.columns(2)

# --- FUNCION ORDEN ---
def enviar_orden(side):
    order_data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": "market",
        "time_in_force": "gtc"
    }

    response = requests.post(
        f"{BASE_URL}/v2/orders",
        headers=headers,
        data=json.dumps(order_data)
    )

    return response

# --- BOTONES ---
if col_buy.button("🟢 COMPRAR"):
    r = enviar_orden("buy")
    if r.status_code == 200:
        st.success("Orden de COMPRA enviada 🚀")
    else:
        st.error(r.text)

if col_sell.button("🔴 VENDER"):
    r = enviar_orden("sell")
    if r.status_code == 200:
        st.success("Orden de VENTA enviada 🚀")
    else:
        st.error(r.text)
