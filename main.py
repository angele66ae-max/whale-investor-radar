import streamlit as st
import yfinance as yf
from alpaca_trade_api.rest import REST

# Sacar llaves de Secrets
API_KEY = st.secrets["ALPACA_API_KEY"]
SECRET_KEY = st.secrets["ALPACA_SECRET_KEY"]
BASE_URL = st.secrets["ALPACA_BASE_URL"]

# Conectar Alpaca
alpaca = REST(API_KEY, SECRET_KEY, BASE_URL)

st.title("🤖 IA Trader: Alpaca Pro")

# Escáner simple
ticker = st.text_input("Empresa para analizar (ej: NVDA):", "NVDA").upper()

if st.button("Analizar y Comprar"):
    data = yf.Ticker(ticker).history(period="1d")
    precio = data['Close'][-1]
    st.write(f"Precio actual: ${precio:.2f}")
    
    try:
        alpaca.submit_order(
            symbol=ticker.replace("-USD", ""),
            qty=1,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        st.success(f"✅ ¡Compra de {ticker} hecha en Alpaca!")
        st.balloons()
    except Exception as e:
        st.error(f"Error: {e}")
