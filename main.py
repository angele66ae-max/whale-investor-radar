import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType

# ------------------ CONFIG ------------------
API_KEY = "TU_API_KEY"
SECRET_KEY = "TU_SECRET_KEY"
BASE_URL = "https://paper-api.alpaca.markets"

trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

st.set_page_config(page_title="Whale Investor Radar PRO", layout="wide")

st.title("🐋 Whale Investor Radar PRO")

# ------------------ SIDEBAR ------------------

symbol = st.sidebar.text_input("Símbolo", value="AAPL", key="symbol_input")
risk_percent = st.sidebar.slider("Riesgo por operación (%)", 1, 20, 10)
take_profit_percent = st.sidebar.slider("Take Profit (%)", 1, 20, 5)
stop_loss_percent = st.sidebar.slider("Stop Loss (%)", 1, 20, 3)

# ------------------ DATOS ------------------

data = yf.download(symbol, period="1mo", interval="1h")

if data.empty:
    st.error("Símbolo inválido")
    st.stop()

data["EMA20"] = data["Close"].ewm(span=20).mean()
data["EMA50"] = data["Close"].ewm(span=50).mean()
data["Volume_MA"] = data["Volume"].rolling(20).mean()

# Whale detection
data["Whale"] = data["Volume"] > data["Volume_MA"] * 2

st.line_chart(data[["Close", "EMA20", "EMA50"]])

if data["Whale"].iloc[-1]:
    st.success("🐋 Posible movimiento de ballena detectado")

# ------------------ SEÑAL ------------------

buy_signal = data["EMA20"].iloc[-1] > data["EMA50"].iloc[-1]
sell_signal = data["EMA20"].iloc[-1] < data["EMA50"].iloc[-1]

# ------------------ CUENTA ------------------

account = trading_client.get_account()
buying_power = float(account.buying_power)

st.metric("💰 Buying Power", f"${buying_power:,.2f}")

capital_to_use = buying_power * (risk_percent / 100)

# ------------------ BOT ------------------

if st.button("🚀 Activar Bot Automático"):

    if buying_power < 50:
        st.warning("⚠️ No hay suficiente poder adquisitivo")
    else:

        if buy_signal:

            order = MarketOrderRequest(
                symbol=symbol,
                notional=capital_to_use,
                side=OrderSide.BUY,
                type=OrderType.MARKET,
                time_in_force=TimeInForce.DAY
            )

            trading_client.submit_order(order_data=order)
            st.success("✅ Orden de COMPRA ejecutada")

        elif sell_signal:

            order = MarketOrderRequest(
                symbol=symbol,
                notional=capital_to_use,
                side=OrderSide.SELL,
                type=OrderType.MARKET,
                time_in_force=TimeInForce.DAY
            )

            trading_client.submit_order(order_data=order)
            st.success("🔴 Orden de VENTA ejecutada")

        else:
            st.info("Sin señal clara")

# ------------------ FONDO MODE ------------------

st.subheader("💼 Fondo Mode")

balance = float(account.equity)
initial_balance = float(account.last_equity)

profit = balance - initial_balance

st.metric("Capital Total", f"${balance:,.2f}")
st.metric("Ganancia/Pérdida", f"${profit:,.2f}")

# ------------------ STOP LOSS & TAKE PROFIT SIMULADO ------------------

last_price = data["Close"].iloc[-1]
take_profit_price = last_price * (1 + take_profit_percent / 100)
stop_loss_price = last_price * (1 - stop_loss_percent / 100)

st.write(f"🎯 Take Profit: ${take_profit_price:,.2f}")
st.write(f"🛑 Stop Loss: ${stop_loss_price:,.2f}")

st.success("Sistema PRO cargado correctamente 🧠🔥")
