import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Angel Capital Quant Fund", layout="wide")
st.title("🏦 Angel Capital Quant Fund")

API_KEY = st.secrets["ALPACA_API_KEY"]
SECRET_KEY = st.secrets["ALPACA_SECRET_KEY"]

trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)

# ---------------- SIDEBAR ----------------
symbol = st.sidebar.text_input("Símbolo", "AAPL")
risk_percent = st.sidebar.slider("Riesgo por operación (%)", 1, 20, 5)
tp_percent = st.sidebar.slider("Take Profit (%)", 1, 20, 5)
sl_percent = st.sidebar.slider("Stop Loss (%)", 1, 20, 3)
auto_trade = st.sidebar.toggle("🤖 Activar Auto Trading")

# ---------------- DATA ----------------
data = yf.download(symbol, period="3mo", interval="1h")

if data.empty:
    st.error("Símbolo inválido o sin datos.")
    st.stop()

# FIX MultiIndex
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)
