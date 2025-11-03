import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import datetime


st.caption(f"Última actualización: {datetime.datetime.now().strftime('%H:%M:%S')}")


# Auto refresh cada 30 segundos (30000 ms)
st_autorefresh(interval=30000, key="datarefresh")

# ------------------------------------------------------
# CONFIGURACIÓN BÁSICA
# ------------------------------------------------------
st.set_page_config(page_title="Dashboard de Leads - Marketing", page_icon="📈", layout="wide")

st.title("📊 Dashboard de Leads - Marketing")
st.markdown("Visualización de leads clasificados automáticamente por la IA 🚀")

API_URL = "https://red-rice-peel.loca.lt/leads"

# ------------------------------------------------------
# CARGA DE DATOS
# ------------------------------------------------------
try:
    res = requests.get(API_URL)
    res.raise_for_status()
    data = res.json()
    leads = pd.DataFrame(data["leads"])

    if leads.empty:
        st.warning("⚠️ No hay leads registrados aún.")
        st.stop()

except Exception as e:
    st.error(f"Error al obtener datos de la API: {e}")
    st.stop()

# ------------------------------------------------------
# MÉTRICAS CLAVE
# ------------------------------------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Leads Totales", len(leads))
col2.metric("Urgencia Alta", len(leads[leads["urgencia"] == "alta"]))
col3.metric("Promedio Score", round(leads["score_final"].mean(), 2))

st.divider()

# ------------------------------------------------------
# GRAFICOS PRINCIPALES
# ------------------------------------------------------

# 1️⃣ Distribución por Urgencia
fig_urgencia = px.histogram(
    leads,
    x="urgencia",
    color="urgencia",
    title="Distribución de Leads por Nivel de Urgencia",
    color_discrete_map={"alta": "red", "media": "orange", "baja": "green"}
)
st.plotly_chart(fig_urgencia, use_container_width=True)

# 2️⃣ Leads por Segmento
# Agrupar por segmento y renombrar columnas
segment_counts = leads["segmento"].value_counts().reset_index()
segment_counts.columns = ["segmento", "count"]

fig_segmento = px.bar(
    segment_counts,
    x="segmento",
    y="count",
    color="segmento",
    title="Leads por Segmento de Interés",
    labels={"segmento": "Segmento", "count": "Cantidad de Leads"}
)
st.plotly_chart(fig_segmento, use_container_width=True)

# 3️⃣ Distribución por Tipo de Cliente
fig_tipo = px.pie(
    leads,
    names="tipo_cliente",
    title="Distribución por Tipo de Cliente",
    color_discrete_sequence=px.colors.sequential.RdBu
)
st.plotly_chart(fig_tipo, use_container_width=True)

# 4️⃣ Score promedio por Fuente
fig_fuente = px.box(
    leads,
    x="canal",
    y="score_final",
    color="canal",
    title="Distribución del Score Final por Canal del Lead",
    labels={"canal": "Canal", "score_final": "Score Final"}
)
st.plotly_chart(fig_fuente, use_container_width=True)

# ------------------------------------------------------
# TABLA FINAL
# ------------------------------------------------------
st.subheader("📋 Leads Recientes")
st.dataframe(
    leads[["nombre", "email", "tipo_cliente", "segmento", "urgencia", "score_final", "canal"]],
    use_container_width=True,
    hide_index=True
)



