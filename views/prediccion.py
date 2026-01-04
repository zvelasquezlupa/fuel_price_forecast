import streamlit as st
import os
from src.train_model import predict_segment
import matplotlib.pyplot as plt
from src.preprocessing import analyze_segment
# ---------------------------------------------------------
# TÍTULO
# ---------------------------------------------------------
st.title("📊 Predicción de Precios de Hidrocarburos")
st.markdown("Selecciona una provincia y un producto, luego ejecute la predicción.")

def run():
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

    # ---------------------------------------------------------
    # 3. BOTÓN PARA EJECUTAR ANÁLISIS
    # ---------------------------------------------------------

    st.markdown("---")
    st.subheader("🔍 Ejecutar Predicción")

    analizar = st.button("📊 Predecir serie seleccionada")
    
    ruta = os.path.join(SEGMENTED_PATH, provincia, producto, "stationary.parquet")

    # Si ya existe, simplemente cargarlo

    if not analizar:
        st.info("Selecciona provincia y producto, luego pulsa **Predecir serie seleccionada**.")
        st.stop()


    # ---------------------------------------------------------
    # 4. Ejecutar predicción bajo demanda
    # ---------------------------------------------------------

    with st.spinner("Ejecutando predicción"):
        df_original, df_stationary, metadata, stationary_flag = analyze_segment(provincia, producto)
        y_test, pred_mean, pred_ci, mae, rmse = predict_segment(provincia, producto)

    st.success("Predicción completada.")

    # ---------------------------------------------------------
    # 5. Visualización de la serie original
    # ---------------------------------------------------------
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
