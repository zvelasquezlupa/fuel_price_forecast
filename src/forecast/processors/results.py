# processors/progress.py
import csv
import os

RESULTS_PATH = "data/model_results.csv"

def init_results_csv():
    """Crea el CSV si no existe, con cabeceras."""
    os.makedirs(os.path.dirname(RESULTS_PATH), exist_ok=True)

    if not os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["provincia", "producto", "modelo", "mae", "rmse", "tiempo"])

def append_result(provincia, producto, modelo, mae, rmse, tiempo):
    """Añade una fila al CSV de resultados."""
    with open(RESULTS_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([provincia, producto, modelo, mae, rmse, tiempo])
