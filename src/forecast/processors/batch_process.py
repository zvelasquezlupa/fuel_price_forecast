# processors/batch_process.py
import threading
from src.analysis.analysis import analisis_estacionaridad
from src.forecast.train_model import predict_segment
from src.utils.helpers import get_productos,get_provincias
from src.forecast.processors.progress import update_progress, init_progress
from src.forecast.processors.results import init_results_csv, append_result


def procesar_todo():
    init_progress()
    init_results_csv()   # <-- NUEVO
    update_progress(status="running", current=None)
    for provincia in get_provincias():
        for producto in get_productos(provincia):
            segmento = f"{provincia} / {producto}"
            try:
                update_progress(current=segmento)
                # 1) Análisis
                #analisis_estacionaridad(provincia, producto)

                # 2) Entrenamiento + predicción
                # --- 1) SARIMAX con exógenas ---
                maesarimax, rmsesarimax, timesarimax = predict_sarimax(provincia, producto)
                append_result(provincia, producto, "sarimax", maesarimax, rmsesarimax, timesarimax)

                # --- 2) SARIMAX sin exógenas ---
                maesinexo, rmsesinexo, timesinexo = predict_sinexo(provincia, producto)
                append_result(provincia, producto, "sarimax_sin_exo", maesinexo, rmsesinexo, timesinexo)

                # --- 3) LSTM ---
                maelstm, rmselstm, timelstm = predict_lstm(provincia, producto)
                append_result(provincia, producto, "lstm", maelstm, rmselstm, timelstm)

                # --- 4) Prophet ---
                maeprop, rmseprop, timeprop = predict_prop(provincia, producto)
                append_result(provincia, producto, "prophet", maeprop, rmseprop, timeprop)

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
