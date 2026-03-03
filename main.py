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
