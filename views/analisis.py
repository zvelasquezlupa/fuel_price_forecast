import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

# Pipelines
from src.analysis import get_analyze, analyze_segment

def run():
    SEGMENTED_PATH = "src/data/segmented"

    # ---------------------------------------------------------
    # TÍTULO
    # ---------------------------------------------------------
    st.title("📊 Análisis de series temporales")
    st.markdown("Para ejecuta el análisis selecciona una provincia y un producto.")

    # ---------------------------------------------------------
    # 1. Cargar provincias y productos
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
    #st.subheader("📊 Ejecutar análisis")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Predecir serie seleccionada"):
            with st.spinner("Ejecutando Análisis"):
                 analyze_segment(provincia,producto)
            st.success("Análisis completado.")

    with col2:
        mostrar_resultados = st.button("🔍 Ver resultados")

    if not mostrar_resultados:
        st.stop()

    # ---------------------------------------------------------
    # 4. Ejecutar análisis bajo demanda
    # ---------------------------------------------------------

    df_original, df_stationary, metadata, stationary_flag = get_analyze(provincia, producto)

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

    estado = "✅ Estacionaria" if stationary_flag else "⚠️ No estacionaria"
    st.info(f"**Serie evaluada como:** {estado}")