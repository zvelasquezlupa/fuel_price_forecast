import streamlit as st
import pandas as pd

st.set_page_config(page_title='predicciones.es', page_icon="smile")
def main():
    st.title("Predicción de Hidrocarburos")
    st.text("Se hará la predicción de dibrocarburos por provincia y tipo de Combustible")

if __name__=='__main__':
    main()