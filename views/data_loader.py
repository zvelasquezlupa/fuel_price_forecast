import streamlit as st
import os
from src.data_preprocessing.data_loader import actualizar_datos, get_datos

def run():
    st.title("🔄 Historico de Precios")

    SEGMENTED_PATH = "src/data/segmented"
    # ---------------------------------------------------------
    # TÍTULO
    # ---------------------------------------------------------
    st.markdown("Para ver los datos selecciona una provincia y un producto.")

    # ---------------------------------------------------------
    # 1. Cargar provincias y productos (CÓDIGO ORIGINAL)
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
    # 3. BOTONES PARA EJECUTAR ANÁLISIS (CÓDIGO ORIGINAL + NUEVO)
    # ---------------------------------------------------------
    mostrar_segmento = st.button("🔍 Ver datos segmento")
    if mostrar_segmento:
        df_segmento= get_datos(provincia,producto)
        if df_segmento is None:
            st.warning("No se encontraron datos para el segmento seleccionado")
        else:
            df_segmento = df_segmento.sort_values("Fecha", ascending=False)
            st.caption(f"Filas: {len(df_segmento)} | Desde {df_segmento['Fecha'].min().date()} hasta {df_segmento['Fecha'].max().date()}")
            st.subheader("📊 Datos segmento")
            st.dataframe(df_segmento, use_container_width=True)   

    st.markdown("---")

    # --- Carga de Excel ---
    archivo = st.file_uploader("Cargar archivo Excel CNMC (por año)", type=["csv"])
    # 1) Actualizar histórico de un segmento
    if archivo and st.button("Actualizar Datos"):
        df=actualizar_datos(archivo)
        st.write("Datos Cargados:")
        st.dataframe(df)
        st.success(f"Histórico actualizado.")

 

