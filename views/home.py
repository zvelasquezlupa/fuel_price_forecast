import streamlit as st
import os
import matplotlib.pyplot as plt

from src.forecast import predict_future_days

def run():
    st.title("Predicción del precio de los carburantes en España")

    st.markdown("""
    ### 📊 Objetivo del proyecto

    Esta aplicación presenta los resultados del análisis y predicción del precio
    de los carburantes en España, a partir de datos oficiales y modelos de series temporales.

    ### 🔎 Qué puedes consultar
    - Predicciones por rango de días
    - Tipo de combustible
    - Municipio
    """)

    SEGMENTED_PATH = "src/data/segmented"
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
    st.info("Esta sección es pública y no requiere autenticación.")

    horizonte = st.selectbox(
        "Horizonte de predicción",
        [30, 60, 90],
        index=0
    )

    if st.button("Generar predicción futura"):
        df_hist, df_pred, metrics = predict_future_days(provincia, producto, horizonte)

        # --- Panel de métricas ---
        st.subheader("📊 Métricas del modelo cargado")
        col1, col2, col3 = st.columns(3)
        col1.metric("AIC", f"{metrics['AIC']:.2f}")
        col2.metric("BIC", f"{metrics['BIC']:.2f}")
        col3.metric("Log-Likelihood", f"{metrics['LogLik']:.2f}")

        # --- Gráfico histórico + futuro ---
        st.subheader("📈 Predicción futura")

        fig, ax = plt.subplots(figsize=(12, 5))

        # Histórico
        ax.plot(df_hist.index, df_hist["Precio"], label="Histórico", color="blue")

        # Futuro
        ax.plot(df_pred.index, df_pred["Predicción"], label="Predicción futura", color="green")
        ax.fill_between(df_pred.index, df_pred["Lower"], df_pred["Upper"],
                        color="lightgreen", alpha=0.3, label="Intervalo confianza")

        ax.set_title(f"{provincia} / {producto} — Predicción {horizonte} días")
        ax.set_ylabel("€/litro")
        ax.legend()

        st.pyplot(fig)

        # --- Botón de descarga ---
        st.subheader("📥 Descargar predicción futura")
        st.download_button(
            label="Descargar como CSV",
            data=df_pred.to_csv().encode("utf-8"),
            file_name=f"prediccion_{provincia}_{producto}_{horizonte}dias.csv",
            mime="text/csv"
        )

        # --- Mostrar tabla ---
        st.dataframe(df_pred)