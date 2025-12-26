import streamlit as st

def run():
    st.title("Predicción del precio de los carburantes en España")

    st.markdown("""
    ### 📊 Objetivo del proyecto

    Esta aplicación presenta los resultados del análisis y predicción del precio
    de los carburantes en España, a partir de datos oficiales y modelos de series temporales.

    ### 🔎 Qué puedes consultar
    - Predicciones por fecha
    - Tipo de combustible
    - Municipio
    """)

    st.info("Esta sección es pública y no requiere autenticación.")
