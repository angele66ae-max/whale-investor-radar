import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType

# -------------------- CONFIG --------------------

API_KEY = "TU_API_KEY"
SECRET_KEY = "TU_SECRET_KEY"

trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

st.set_page_config(page_title="Angel Capital Quant Fund", layout="wide")
st.title("🏦 Angel Capital Quant Fund")

# -------------------- SIDEBAR --------------------

symbol = st.sidebar.text_input("Símbolo", "AAPL", key="symbol")
risk_percent = st.sidebar.slider("Riesgo por operación (%)", 1, 20, 5)
tp_percent = st.sidebar.slider("Take Profit (%)", 1, 20, 5)
sl_percent = st.sidebar.slider("Stop Loss (%)", 1, 20, 3)
auto_trade = st.sidebar.toggle("🤖 Activar Auto Trading")

# -------------------- DATA --------------------

data = yf.download(symbol, period="3mo", interval="1h")

if data.empty:
    st.error("Símbolo inválido")
    st.stop()

data["EMA20"] = data["Close"].ewm(span=20).mean()
data["EMA50"] = data["Close"].ewm(span=50).mean()
data["Vol_MA"] = data["Volume"].rolling(20).mean()
data["Whale"] = data["Volume"] > data["Vol_MA"] * 2

st.line_chart(data[["Close", "EMA20", "EMA50"]])

# -------------------- SEÑALES --------------------

buy_signal = data["EMA20"].iloc[-1] > data["EMA50"].iloc[-1]
sell_signal = data["EMA20"].iloc[-1] < data["EMA50"].iloc[-1]

if data["Whale"].iloc[-1]:
    st.success("🐋 Whale Movement Detected")

# -------------------- CUENTA --------------------

account = trading_client.get_account()
buying_power = float(account.buying_power)
equity = float(account.equity)
last_equity = float(account.last_equity)

st.metric("💰 Buying Power", f"${buying_power:,.2f}")
st.metric("🏦 Equity", f"${equity:,.2f}")

profit = equity - last_equity
st.metric("📈 Daily P/L", f"${profit:,.2f}")

# -------------------- RISK MANAGEMENT --------------------

capital_to_use = buying_power * (risk_percent / 100)

if capital_to_use < 50:
    st.warning("Capital muy bajo para operar")

# -------------------- ORDEN INTELIGENTE --------------------

def place_order(side):
    try:
        order = MarketOrderRequest(
            symbol=symbol,
            notional=capital_to_use,
            side=side,
            type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY
        )
        trading_client.submit_order(order_data=order)
        st.success(f"Orden {side.name} ejecutada correctamente")
    except Exception as e:
        st.error(f"Error: {e}")

# -------------------- BOT --------------------

if auto_trade:
    if buy_signal and capital_to_use > 50:
        place_order(OrderSide.BUY)
    elif sell_signal and capital_to_use > 50:
        place_order(OrderSide.SELL)

# -------------------- STOP & TAKE PROFIT (REAL CALCULATION) --------------------

last_price = data["Close"].iloc[-1]
tp_price = last_price * (1 + tp_percent / 100)
sl_price = last_price * (1 - sl_percent / 100)

st.write(f"🎯 Take Profit: ${tp_price:,.2f}")
st.write(f"🛑 Stop Loss: ${sl_price:,.2f}")

# -------------------- BACKTEST SIMPLE --------------------

st.subheader("📊 Backtesting Simple")

data["Signal"] = np.where(data["EMA20"] > data["EMA50"], 1, -1)
data["Returns"] = data["Close"].pct_change()
data["Strategy"] = data["Signal"].shift(1) * data["Returns"]

strategy_return = (1 + data["Strategy"]).cumprod()

st.line_chart(strategy_return)

st.success("Sistema institucional activo 🧠")
