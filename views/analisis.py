import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

# Pipelines
from src.etl.pipelineclean import build_base_parquets
from src.preprocessing import analyze_segment

def run():
    RAW_PATH = "src/data/raw"
    SEGMENTED_PATH = "src/data/segmented"

    # ---------------------------------------------------------
    # TÍTULO
    # ---------------------------------------------------------
    st.title("📊 Análisis de series temporales")
    st.markdown("Selecciona una provincia y un producto, luego ejecuta el análisis.")

    # ---------------------------------------------------------
    # 1. Verificar si existen datos segmentados
    # ---------------------------------------------------------

    def segmented_data_exists():
        return os.path.exists(SEGMENTED_PATH) and len(os.listdir(SEGMENTED_PATH)) > 0

    if not segmented_data_exists():
        st.warning("No se encontraron datos segmentados. Procesando archivos CSV…")
        build_base_parquets(RAW_PATH)
        st.success("Datos segmentados correctamente. Ya puedes analizar las series.")

    # ---------------------------------------------------------
    # 2. Cargar provincias y productos
    # ---------------------------------------------------------

    provincias = sorted([
        d for d in os.listdir(SEGMENTED_PATH)
        if os.path.isdir(os.path.join(SEGMENTED_PATH, d))
    ])

    if not provincias:
        st.error("No se encontraron provincias procesadas.")
        st.stop()

    provincia = st.selectbox("Provincia", provincias)

    productos = sorted([
        d for d in os.listdir(os.path.join(SEGMENTED_PATH, provincia))
        if os.path.isdir(os.path.join(SEGMENTED_PATH, provincia, d))
    ])

    if not productos:
        st.error("No se encontraron productos para esta provincia.")
        st.stop()

    producto = st.selectbox("Producto", productos)

    # ---------------------------------------------------------
    # 3. BOTÓN PARA EJECUTAR ANÁLISIS
    # ---------------------------------------------------------

    st.markdown("---")
    st.subheader("🔍 Ejecutar análisis")

    analizar = st.button("📊 Analizar serie seleccionada")

    if not analizar:
        st.info("Selecciona provincia y producto, luego pulsa **Analizar serie seleccionada**.")
        st.stop()

    # ---------------------------------------------------------
    # 4. Ejecutar análisis bajo demanda
    # ---------------------------------------------------------

    with st.spinner("Ejecutando análisis estadístico…"):
        df_original, df_stationary, metadata, stationary_flag = analyze_segment(provincia, producto)

    st.success("Análisis completado.")

    # ---------------------------------------------------------
    # 5. Visualización de la serie original
    # ---------------------------------------------------------
    st.subheader("📈 Serie original")
    fig1 = px.line(
        df_original,
        x="Fecha",
        y="Precio",
        title=f"Precio diario — {provincia} / {producto}"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # ---------------------------------------------------------
    # 6. Visualización de la serie transformada (si aplica)
    # ---------------------------------------------------------

    if not stationary_flag:
        st.subheader("🔁 Serie transformada (diferenciada)")
        fig2 = px.line(
            df_stationary,
            x="Fecha",
            y="Precio",
            title="Serie diferenciada"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.success("La serie ya es estacionaria. No fue necesario diferenciarla.")

    # ---------------------------------------------------------
    # 7. Resultados estadísticos
    # ---------------------------------------------------------

    st.subheader("📊 Resultados de estacionariedad")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("ADF p-value", f"{metadata['adf']['pvalue']:.4f}")
        st.metric("ADF stat", f"{metadata['adf']['stat']:.2f}")

    with col2:
        st.metric("KPSS p-value", f"{metadata['kpss']['pvalue']:.4f}")
        st.metric("KPSS stat", f"{metadata['kpss']['stat']:.2f}")

    estado = "✅ Estacionaria" if metadata["stationary"] else "⚠️ No estacionaria"
    st.info(f"**Serie evaluada como:** {estado}")