import streamlit as st

def run():
    st.title("Análisis exploratorio")

    st.markdown("""
    Aquí se presenta:
    - Análisis de tendencia
    - Estacionalidad
    - Pruebas ADF y KPSS
    """)

    st.success("Aquí luego conectas tus gráficos")
