
# processors/progress.py

import json
import os
from src.utils.config import PROGRESS_PATH


def init_progress():
    """Inicializa el archivo de progreso si no existe."""
    if not os.path.exists(os.path.dirname(PROGRESS_PATH)):
        os.makedirs(os.path.dirname(PROGRESS_PATH), exist_ok=True)

    if not os.path.exists(PROGRESS_PATH):
        data = {
            "status": "idle",      # idle | running | finished | error
            "current": None,       # segmento actual "Provincia / Producto"
            "completed": [],       # lista de segmentos completados
            "errors": []           # lista de mensajes de error
        }
        with open(PROGRESS_PATH, "w") as f:
            json.dump(data, f, indent=4)


    def load_progress():
        """Lee el archivo de progreso."""
        init_progress()
        with open(PROGRESS_PATH, "r") as f:
            return json.load(f)


    def save_progress(data):
        """Guarda el archivo de progreso."""
        with open(PROGRESS_PATH, "w") as f:
            json.dump(data, f, indent=4)


    def update_progress(status=None, current=None, completed=None, error=None):
        """
        Actualiza campos específicos del progreso.
        - status: "idle" | "running" | "finished" | "error"
        - current: string del segmento actual
        - completed: string de segmento completado para añadir a la lista
        - error: string de error para añadir a la lista
        """
        data = load_progress()

        if status is not None:
            data["status"] = status

        if current is not None:
            data["current"] = current

        if completed is not None:
            if completed not in data["completed"]:
                data["completed"].append(completed)

        if error is not None:
            data["errors"].append(error)

        save_progress(data)