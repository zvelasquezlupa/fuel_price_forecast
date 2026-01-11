# config.py

import os

# Carpeta base donde están los segmentos (provincias/productos)
BASE_PATH = "src/data"
SEGMENTED_PATH = os.path.join(BASE_PATH, "segmented")

# Archivo de progreso para el procesamiento masivo
PROGRESS_PATH = os.path.join(BASE_PATH, "progress.json")