import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="IA Wealth Master", page_icon="💰")

st.title("💰 IA de Estrategia de Inversión")

# Lista expandida de activos rentables
activos = {
    "Acciones Top": ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "META"],
    "Criptomonedas": ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "BNB-USD"],
    "Materias Primas": ["GC=F", "CL=F"] # Oro y Petróleo
}

st.sidebar.header("Configuración de la IA")
categoria = st.sidebar.selectbox("Selecciona Mercado", list(activos.keys()))

if st.button(f"Analizar Rentabilidad de {categoria}"):
    resultados = []
    with st.spinner('La IA está escaneando el mercado...'):
        for ticker in activos[categoria]:
            data = yf.Ticker(ticker).history(period="1mo")
            if not data.empty:
                cambio = ((data['Close'][-1] - data['Close'][0]) / data['Close'][0]) * 100
                precio_actual = data['Close'][-1]
                # Lógica simple de IA: Si subió más de 5%, es 'Compra Fuerte'
                señal = "COMPRA" if cambio > 5 else "MANTENER" if cambio > 0 else "VENTA"
                
                resultados.append({
                    "Símbolo": ticker,
                    "Precio": round(precio_actual, 2),
                    "Rendimiento (%)": round(cambio, 2),
                    "Recomendación IA": señal
                })
    
    df = pd.DataFrame(resultados).sort_values(by="Rendimiento (%)", ascending=False)
    st.table(df)
    
    mejor = df.iloc[0]
    st.success(f"🌟 La IA detectó la mayor oportunidad en: **{mejor['Símbolo']}**")

st.warning("⚠️ Para activar la 'Inversión Automática', necesitamos conectar una API de Binance, Bitso o Interactive Brokers.")
