import streamlit as st
from src.data_manager import actualizar_datos
from src.processors.batch_process import procesar_todo

def run():
    st.title("🔄 Actualización de datos y procesamiento masivo")

    # --- Carga de Excel ---
    archivo = st.file_uploader("Cargar archivo Excel CNMC (por año)", type=["csv"])
    # 1) Actualizar histórico de un segmento
    if archivo and st.button("Actualizar histórico para este segmento"):
        df=actualizar_datos(archivo)
        st.write("Datos Cargados:")
        st.dataframe(df)
        st.success(f"Histórico actualizado.")
