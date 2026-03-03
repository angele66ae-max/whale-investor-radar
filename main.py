import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="IA Inversora Pro", page_icon="🤖")

st.title("🤖 IA de Selección de Activos")
st.markdown("---")

# 1. Función para que la IA califique una inversión
def analizar_activo(ticker):
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="1mo")
        # Calculamos rendimiento del último mes
        rendimiento = ((hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0]) * 100
        return round(rendimiento, 2)
    except:
        return None

# 2. Panel de Control de la IA
st.subheader("🚀 Radar de Rentabilidad Automático")
activos_a_monitorear = ["NVDA", "AAPL", "TSLA", "BTC-USD", "ETH-USD", "SOL-USD", "MSFT"]

if st.button("Escanear Mercado ahora"):
    resultados = []
    for a in activos_a_monitorear:
        score = analizar_activo(a)
        if score is not None:
            resultados.append({"Activo": a, "Rendimiento Mes (%)": score})
    
    df_ranking = pd.DataFrame(resultados).sort_values(by="Rendimiento Mes (%)", ascending=False)
    
    # La IA recomienda el mejor
    mejor = df_ranking.iloc[0]
    st.success(f"✅ La IA recomienda: **{mejor['Activo']}** con un {mejor['Rendimiento Mes (%)']}% este mes.")
    st.table(df_ranking)

st.markdown("---")
st.info("⚠️ Nota: Para que la IA invierta sola (Trading Automático), necesitaríamos conectar una cuenta de un Broker (como Binance o Alpaca) mediante una 'API Key'. Eso es el siguiente paso después de tener el radar listo.")
