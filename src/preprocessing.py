import os
import pandas as pd
import json
from src.stats.stationarity import adf_test, kpss_test, is_stationary
from src.stats.transformations import difference
from src.persistence.file_store import save_parquet, save_metadata

def to_native(obj):
    if hasattr(obj, "item"):
        return obj.item()  # numpy → python
    return obj

def analyze_segment(provincia, producto):
    base_path = f"src/data/segmented/{provincia}/{producto}/"
    original_path = base_path + "original.parquet"
    stationary_path = base_path + "stationary.parquet"
    metadata_path = base_path + "metadata.json"

    df = pd.read_parquet(original_path)

    # Asegurar que la fecha sea índice
   
    df_limpio=df[["Fecha", "Precio"]].copy()
    df_limpio = df_limpio.set_index("Fecha").sort_index()
    serie = df_limpio["Precio"]
    serie.index = pd.to_datetime(serie.index)
    print(serie)
    print(type(serie))
    print(type(serie.index))

    adf = adf_test(serie)
    kpss = kpss_test(serie)
    stationary_flag = is_stationary(adf, kpss)

    if stationary_flag:
        df_stationary = df[["Fecha", "Precio"]].copy()
    else:
        df_stationary = difference(serie)
        df_stationary = df_stationary.reset_index()

    save_parquet(df_stationary, stationary_path)

    # ✅ Conversión segura con to_native
    metadata = {
        "provincia": provincia,
        "producto": producto,
        "adf": {k: to_native(v) for k, v in adf.items()},
        "kpss": {k: to_native(v) for k, v in kpss.items()},
        "stationary": bool(stationary_flag)
    }

    save_metadata(metadata, metadata_path)

    return df, df_stationary, metadata, stationary_flag