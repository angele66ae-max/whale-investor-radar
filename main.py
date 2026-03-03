import streamlit as st
import yfinance as yf
from alpaca_trade_api.rest import REST

# Esto saca las llaves de la "caja fuerte" que configuraste arriba
API_KEY = st.secrets["ALPACA_API_KEY"]
SECRET_KEY = st.secrets["ALPACA_SECRET_KEY"]
BASE_URL = st.secrets["ALPACA_BASE_URL"]

# Conectamos con Alpaca
alpaca = REST(API_KEY, SECRET_KEY, BASE_URL)

st.title("🤖 Mi IA Inversora")

# Elegimos qué comprar
ticker = st.selectbox("¿Qué quieres que compre la IA?", ["NVDA", "AAPL", "BTC-USD", "ETH-USD"])

if st.button("🚀 EJECUTAR COMPRA"):
    try:
        # Enviamos la orden de compra a Alpaca
        # Nota: Para cripto en Alpaca se quita el "-USD"
        simbolo_limpio = ticker.replace("-USD", "")
        
        alpaca.submit_order(
            symbol=simbolo_limpio,
            qty=1, # Compra 1 unidad
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        st.balloons()
        st.success(f"¡Éxito! Compramos 1 unidad de {simbolo_limpio} en Alpaca.")
    except Exception as e:
        st.error(f"Algo salió mal: {e}")
