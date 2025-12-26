import streamlit as st

def init_session():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "redirect_after_login" not in st.session_state:
        st.session_state.redirect_after_login = "Home"

def login(username, password):
    if username == "admin" and password == "admin":
        st.session_state.authenticated = True
        return True
    return False

def logout():
    st.session_state.authenticated = False
