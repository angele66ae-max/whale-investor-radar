import streamlit as st
import yfinance as yf
from alpaca_trade_api.rest import REST

# Sacamos las llaves de la "caja fuerte"
API_KEY = st.secrets["ALPACA_API_KEY"]
SECRET_KEY = st.secrets["ALPACA_SECRET_KEY"]
BASE_URL = st.secrets["ALPACA_BASE_URL"]

# Conexión con Alpaca
alpaca = REST(API_KEY, SECRET_KEY, BASE_URL)

st.title("🤖 Mi IA Inversora")

# Selector de activo
ticker = st.selectbox("¿Qué quieres comprar?", ["NVDA", "AAPL", "TSLA"])

if st.button("🚀 INVERTIR AHORA"):
    try:
        alpaca.submit_order(
            symbol=ticker,
            qty=1,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        st.success(f"¡Orden enviada! Compraste 1 de {ticker} en Alpaca.")
        st.balloons()
    except Exception as e:
        st.error(f"Error: {e}")
