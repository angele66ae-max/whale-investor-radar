import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json

# ------------------ CONFIG ------------------
st.set_page_config(layout="wide")
st.title("Angel Trader PRO 🔥")

# ------------------ SECRETS ------------------
API_KEY = st.secrets["ALPACA_API_KEY"]
SECRET_KEY = st.secrets["ALPACA_SECRET_KEY"]

BASE_URL = "https://paper-api.alpaca.markets"

headers = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY,
    "Content-Type": "application/json"
}

# ------------------ SIDEBAR ------------------
symbol = st.sidebar.text_input("Símbolo", "AAPL", key="symbol")
interval = st.sidebar.selectbox("Timeframe", ["5m", "15m", "1h", "1d"], key="interval")

if interval in ["5m", "15m"]:
    period = "5d"
elif interval == "1h":
    period = "1mo"
else:
    period = "6mo"

# ------------------ DATOS ------------------
data = yf.download(tickers=symbol, period=period, interval=interval)

# ------------------ INDICADORES ------------------
data["EMA9"] = data["Close"].ewm(span=9).mean()
data["EMA21"] = data["Close"].ewm(span=21).mean()

delta = data["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)

avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()

rs = avg_gain / avg_loss
data["RSI"] = 100 - (100 / (1 + rs))

data["Signal"] = 0
data.loc[data["EMA9"] > data["EMA21"], "Signal"] = 1
data.loc[data["EMA9"] < data["EMA21"], "Signal"] = -1

# ------------------ GRAFICO ------------------
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    row_heights=[0.7, 0.3],
    vertical_spacing=0.05
)

fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"],
    name="Precio"
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=data.index,
    y=data["EMA9"],
    name="EMA 9"
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=data.index,
    y=data["EMA21"],
    name="EMA 21"
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=data.index,
    y=data["RSI"],
    name="RSI"
), row=2, col=1)

fig.add_hline(y=70, line_dash="dash", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", row=2, col=1)

fig.update_layout(
    template="plotly_dark",
    xaxis_rangeslider_visible=False,
    height=800
)

st.plotly_chart(fig, use_container_width=True)

# ------------------ SEÑAL ACTUAL ------------------
last_signal = data["Signal"].iloc[-1]

if last_signal == 1:
    st.success("🟢 Señal actual: COMPRA")
elif last_signal == -1:
    st.error("🔴 Señal actual: VENTA")
else:
    st.warning("⚪ Sin señal clara")

# ------------------ CUENTA ------------------
st.markdown("---")
st.header("Trading en Vivo (Paper)")

account = requests.get(f"{BASE_URL}/v2/account", headers=headers).json()

col1, col2, col3 = st.columns(3)

col1.metric("💰 Portfolio", f"${float(account['portfolio_value']):,.2f}")
col2.metric("💵 Cash", f"${float(account['cash']):,.2f}")
col3.metric("⚡ Buying Power", f"${float(account['buying_power']):,.2f}")

# ------------------ ORDENES ------------------
st.markdown("---")

qty = st.number_input("Cantidad de acciones", min_value=1, value=1, key="qty")
stop_loss_pct = st.number_input("Stop Loss (%)", min_value=0.1, value=1.0, key="sl")
take_profit_pct = st.number_input("Take Profit (%)", min_value=0.1, value=2.0, key="tp")

def enviar_orden(side):
    last_price = float(data["Close"].iloc[-1])

    if side == "buy":
        stop_price = round(last_price * (1 - stop_loss_pct/100), 2)
        take_price = round(last_price * (1 + take_profit_pct/100), 2)
    else:
        stop_price = round(last_price * (1 + stop_loss_pct/100), 2)
        take_price = round(last_price * (1 - take_profit_pct/100), 2)

    order_data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": "market",
        "time_in_force": "gtc",
        "order_class": "bracket",
        "take_profit": {
            "limit_price": take_price
        },
        "stop_loss": {
            "stop_price": stop_price
        }
    }

    return requests.post(
        f"{BASE_URL}/v2/orders",
        headers=headers,
        json=order_data
    )

col_buy, col_sell = st.columns(2)

if col_buy.button("🟢 COMPRAR", key="buy"):
    r = enviar_orden("buy")
    if r.status_code == 200:
        st.success("Orden BUY con SL/TP enviada 🚀")
    else:
        st.error(r.text)

if col_sell.button("🔴 VENDER", key="sell"):
    r = enviar_orden("sell")
    if r.status_code == 200:
        st.success("Orden SELL con SL/TP enviada 🚀")
    else:
        st.error(r.text)
