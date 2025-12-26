import streamlit as st
from src.auth.auth import login

def run():
    st.title("🔐 Iniciar sesión")

    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")

    if st.button("Entrar"):
        if login(user, pwd):
            st.success("Sesión iniciada")
            st.rerun()
        else:
            st.error("Credenciales incorrectas")