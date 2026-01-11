import streamlit as st
from src.auth.auth import init_session, logout
from views import home, login, analisis, prediccion, configuracion, data_manager, procesamiento_masivo

st.set_page_config(
    page_title='predicciones.es', 
    page_icon="⛽",
    layout="wide"
)

init_session()

# ---------- MENÚ LATERAL ----------
#st.sidebar.title("🧭 Navegación")

if st.session_state.authenticated:

    option = st.sidebar.radio(
        "Menú",
        ["Home", "Análisis", "Predicciones", "Configuración", "Datos", "Precesamiento Masivo"]
    )

    if st.sidebar.button("🔓 Cerrar sesión"):
        logout()
        st.rerun()

else:
    option = st.sidebar.radio(
        "Menú",
        ["Home", "Login"]
    )

# ---------- RENDER VISTAS ----------
if option == "Home":
    home.run()

elif option == "Login":
    login.run()

elif option == "Análisis":
    if st.session_state.authenticated:
        analisis.run()
    else:
        st.warning("Debes iniciar sesión")
        login.run()

elif option == "Predicciones":
    if st.session_state.authenticated:
        prediccion.run()
    else:
        st.warning("Debes iniciar sesión")
        login.run()

elif option == "Configuración":
    if st.session_state.authenticated:
        configuracion.run()
    else:
        st.warning("Debes iniciar sesión")
        login.run()
elif option == "Datos":
    if st.session_state.authenticated:
        data_manager.run()
    else:
        st.warning("Debes iniciar sesión")
        login.run()
elif option == "Precesamiento Masivo":
    if st.session_state.authenticated:
        procesamiento_masivo.run()
    else:
        st.warning("Debes iniciar sesión")
        login.run()