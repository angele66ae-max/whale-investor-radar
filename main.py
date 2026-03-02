import streamimport streamlit as st
import yfinance as yf

st.title("🐋 Radar de Ballenas")
ticker = st.text_input("Sigla de la empresa (ej: NVDA):", "NVDA").upper()

if ticker:
    stock = yf.Ticker(ticker)
    st.subheader(f"Grandes Inversionistas en {ticker}")
    df = stock.institutional_holders
    if df is not None:
        st.dataframe(df)
    else:
        st.write("No hay datos públicos.")
