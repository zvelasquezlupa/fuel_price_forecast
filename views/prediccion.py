import streamlit as st
import os
from src.train_model import get_predict, predict_segment
import matplotlib.pyplot as plt

def run():
    SEGMENTED_PATH = "src/data/segmented"
    # ---------------------------------------------------------
    # TÍTULO
    # ---------------------------------------------------------
    st.title("📊 Predicción de Precios de Carburantes")
    st.markdown("Para ejecuta la predicción selecciona una provincia y un producto.")

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
    #st.subheader("📊 Ejecutar Predicción")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Predecir serie seleccionada"):
            with st.spinner("Ejecutando predicción"):
                 predict_segment(provincia,producto)
            st.success("Predicción completada.")

    with col2:
        mostrar_resultados = st.button("🔍 Ver resultados")

    if not mostrar_resultados:
        st.stop()
    
    y_test, pred_mean, pred_ci, mae, rmse = get_predict(provincia, producto)
    # ---------------------------------------------------------
    # 5. Visualización de la serie original
    # ---------------------------------------------------------
    if mostrar_resultados:
        st.write("MAE:", mae)
        st.write("RMSE:", rmse)

        # --- Visualización ---
        fig, ax = plt.subplots(figsize=(10,5))
        y_test.plot(ax=ax, label="Real", color="blue")
        pred_mean.plot(ax=ax, label="Predicción", color="red")
        ax.fill_between(pred_ci.index,
                        pred_ci.iloc[:,0],
                        pred_ci.iloc[:,1],
                        color="pink", alpha=0.3)
        ax.set_title(f"Predicción de precios - {provincia} / {producto}")
        ax.legend()
        st.pyplot(fig)
