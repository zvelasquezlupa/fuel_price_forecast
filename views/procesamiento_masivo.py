# views/procesamiento_masivo.py

import streamlit as st
import time
from src.processors.batch_process import procesar_todo_background
from src.processors.progress import load_progress, init_progress

def view_progress():
    """Vista que muestra el progreso en tiempo (casi) real."""
    init_progress()
    progress_data = load_progress()

    st.subheader("Estado general")
    st.write(f"**Estado:** {progress_data['status']}")
    st.write(f"**Procesando:** {progress_data['current']}")

    st.subheader("Segmentos completados")
    if progress_data["completed"]:
        st.write(f"Total: {len(progress_data['completed'])}")
        st.write(progress_data["completed"])
    else:
        st.write("Ningún segmento completado aún.")

    st.subheader("Errores")
    if progress_data["errors"]:
        st.write(progress_data["errors"])
    else:
        st.write("Sin errores registrados por el momento.")

    # Si ya terminó, no recargar automáticamente
    if progress_data["status"] in ("finished", "error", "idle"):
        if progress_data["status"] == "finished":
            st.success("Procesamiento masivo completado.")
        elif progress_data["status"] == "error":
            st.error("El procesamiento terminó con errores. Revisa los detalles arriba.")
        return

    # Auto-refresh cada 2 segundos
    time.sleep(2)
    st.rerun()


def run():
    st.title("⚙️ Procesamiento masivo (análisis + predicción)")

    st.markdown("""
    Esta vista ejecuta el análisis y la predicción para **todos los segmentos**
    (todas las provincias y productos presentes en la carpeta `segmented`).
    """)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🚀 Iniciar procesamiento masivo"):
            procesar_todo_background()
            st.success("Procesamiento iniciado en segundo plano.")

    with col2:
        if st.button("🔄 Reiniciar estado de progreso"):
            init_progress()
            st.success("Estado de progreso reiniciado.")

    st.markdown("---")
    view_progress()