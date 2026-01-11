import streamlit as st
import os
import plotly.graph_objects as go

from src.forecast import predict_future_days

def run():
    st.title("Predicción del precio de los carburantes en España")

    st.markdown("""
    ### 🔎 Consultar el precio del carburante
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

    horizonte = st.selectbox(
        "Horizonte de predicción",
        [30, 60, 90, 120],
        index=0
    )
    if st.button("Generar"):
        df_hist, df_pred, metrics = predict_future_days(provincia, producto, horizonte)

        # --- Métricas ---
        """
        st.subheader("📊 Métricas del modelo")
        col1, col2, col3 = st.columns(3)
        col1.metric("AIC", f"{metrics['AIC']:.2f}")
        col2.metric("BIC", f"{metrics['BIC']:.2f}")
        col3.metric("LogLik", f"{metrics['LogLik']:.2f}")
        """

        # --- Gráfico interactivo ---
        st.subheader("📈 Predicción (€/litro)")

        fig = go.Figure()

        # Histórico
        fig.add_trace(go.Scatter(
            x=df_hist.index,
            y=df_hist["Precio"],
            mode="lines",
            name="Histórico",
            line=dict(color="blue")
        ))

        # Predicción
        fig.add_trace(go.Scatter(
            x=df_pred.index,
            y=df_pred["Predicción"],
            mode="lines",
            name="Predicción futura",
            line=dict(color="green")
        ))

        # Intervalo
        fig.add_trace(go.Scatter(
            x=list(df_pred.index) + list(df_pred.index[::-1]),
            y=list(df_pred["Upper"]) + list(df_pred["Lower"][::-1]),
            fill="toself",
            fillcolor="rgba(0,255,0,0.2)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            name="Intervalo confianza"
        ))

        fig.update_layout(
            yaxis_title="€/litro",
            hovermode="x unified",
            title=f"{provincia} / {producto} — Predicción {horizonte} días"
        )

        st.plotly_chart(fig, use_container_width=True)

        df_pred = df_pred.rename(columns={
            "Lower": "Limite Inferior",
            "Upper": "Limite Superior"
        })

        df_pred.index.name = "Fecha"

        # --- Descargar ---s
        st.download_button(
            "Descargar predicción (CSV)",
            df_pred.to_csv().encode("utf-8"),
            file_name=f"prediccion_{provincia}_{producto}_{horizonte}dias.csv"
        )

        st.dataframe(df_pred)
