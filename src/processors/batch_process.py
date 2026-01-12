# processors/batch_process.py
import threading
from src.analysis import analisis_estacionaridad
from src.train_model import predict_segment
from src.utils.helpers import get_productos,get_provincias
from src.processors.progress import update_progress, init_progress


def procesar_todo():
    init_progress()
    update_progress(status="running", current=None)
    for provincia in get_provincias():
        for producto in get_productos(provincia):
            segmento = f"{provincia} / {producto}"
            try:
                update_progress(current=segmento)
                # 1) Análisis
                analisis_estacionaridad(provincia, producto)

                # 2) Entrenamiento + predicción
                mae, rmse = predict_segment(provincia, producto)

                update_progress(completed=segmento)

            except Exception as e:
                update_progress(error=f"{segmento}: {str(e)}")

    update_progress(status="finished", current=None)

def procesar_todo_background():
    """
    Lanza el procesamiento masivo en un hilo en segundo plano.
    Esta función es la que se llamará desde la vista de Streamlit.
    """
    thread = threading.Thread(target=procesar_todo, daemon=True)
    thread.start()
