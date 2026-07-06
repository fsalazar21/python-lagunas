import streamlit as st
import plotly.graph_objects as go
import numpy as np

from datos import RENTABILIDAD
from calculos import valor_futuro, apv_optimo, cobertura
from recomendador import recomendar

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="Simulador AFP", layout="wide")

st.title("💰 Simulador de Lagunas Previsionales")
st.write("Demo interactiva tipo recomendador financiero")

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.header("👤 Cliente")

ingreso = st.sidebar.number_input("Ingreso mensual", value=1200000)
brecha = st.sidebar.number_input("Brecha previsional", value=15000000)

st.sidebar.header("🎛️ Simulación")

apv = st.sidebar.slider("APV mensual", 5000, 200000, 25000, step=1000)
años = st.sidebar.slider("Horizonte (años)", 1, 40, 15)
fondo = st.sidebar.selectbox("Fondo", ["A","B","C","D","E"])

rent = RENTABILIDAD[fondo]

# ---------------------------
# CÁLCULOS
# ---------------------------
vf = valor_futuro(apv, rent, años)
cov = cobertura(vf, brecha)
apv_opt = apv_optimo(brecha, rent, años)

# ---------------------------
# KPIs
# ---------------------------
st.subheader("📊 Resultados")

c1, c2, c3 = st.columns(3)

c1.metric("Valor Futuro", f"${vf:,.0f}")
c2.metric("Cobertura", f"{cov:.1%}")
c3.metric("APV óptimo", f"${apv_opt:,.0f}")

# ---------------------------
# SEMÁFORO
# ---------------------------
if cov >= 1:
    st.success("✅ Cierra la brecha")
elif cov >= 0.8:
    st.warning("🟡 Cerca de cerrar")
else:
    st.error("🔴 Insuficiente")

# ---------------------------
# GRÁFICO EVOLUCIÓN
# ---------------------------
st.subheader("📈 Evolución")

años_range = list(range(1, años+1))
vf_series = [valor_futuro(apv, rent, x) for x in años_range]

fig = go.Figure()
fig.add_trace(go.Scatter(x=años_range, y=vf_series, mode='lines'))

fig.add_hline(y=brecha)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# SENSIBILIDAD
# ---------------------------
st.subheader("📊 Sensibilidad APV")

apv_vals = np.linspace(5000, 100000, 20)
cov_vals = [cobertura(valor_futuro(a, rent, años), brecha) for a in apv_vals]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=apv_vals, y=cov_vals))

st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# RECOMENDADOR
# ---------------------------
st.subheader("🤖 Recomendación")

resultado = recomendar(
    brecha=brecha,
    ingreso=ingreso,
    apv=apv,
    años=años,
    fondo=fondo
)

c4, c5, c6 = st.columns(3)

c4.metric("Fondo recomendado", resultado["fondo_recomendado"])
c5.metric("APV recomendado", f"${resultado['apv_recomendado']:,.0f}")
c6.metric("Score", f"{resultado['score']}/100")

st.write(f"**Canal:** {resultado['canal']}")
st.write(f"**Prioridad:** {resultado['prioridad']}")
st.write(f"**Horizonte recomendado:** {resultado['horizonte_recomendado']} años")

# ---------------------------
# REGLAS ACTIVADAS
# ---------------------------
st.subheader("📋 Reglas activadas")

for r in resultado["reglas_activadas"]:
    st.write("-", r)