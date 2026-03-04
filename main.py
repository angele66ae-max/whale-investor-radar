# ---------------- DATA ----------------
data = yf.download(symbol, period="3mo", interval="1h")

if data.empty:
    st.error("Símbolo inválido o sin datos.")
    st.stop()

# 🔥 FIX PARA MULTIINDEX
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

# ---------------- INDICADORES ----------------
data["EMA20"] = data["Close"].ewm(span=20).mean()
data["EMA50"] = data["Close"].ewm(span=50).mean()
data["Vol_MA"] = data["Volume"].rolling(20).mean()

data = data.dropna()

data["Whale"] = data["Volume"] > (data["Vol_MA"] * 2)
