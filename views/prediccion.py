import streamlit as st

def run():
    st.title("Predicciones")

    provincia = st.selectbox("Provincia", ["Madrid", "Barcelona"])
    combustible = st.selectbox("Combustible", ["Gasolina 95", "Gasóleo A"])
    fecha = st.date_input("Fecha")

    if st.button("Calcular predicción"):
        st.write("🔮 Predicción simulada:")
        st.metric("Precio estimado (€)", "1.75")
