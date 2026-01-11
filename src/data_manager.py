import pandas as pd
import os
from src.etl.clean import clean_data
from src.etl.segment import segment_by_province_product
def actualizar_datos(file):
    df_csv = pd.read_csv(file, sep=";")
    df = clean_data(df_csv)

    segments = segment_by_province_product(df)

    for (provincia, producto), data in segments.items():
           
        if data.empty:
            continue

        if "/" in provincia:
            provincia=provincia.split("/")[0]

        ruta = f"src/data/segmented/{provincia}/{producto}/original.parquet"
        
        #crear el directorio si no existe
        os.makedirs(os.path.dirname(ruta), exist_ok=True)

        # Cargar histórico existente o crear uno vacío
        if os.path.exists(ruta):
            df_actual = pd.read_parquet(ruta)
            df_actual["Fecha"] = pd.to_datetime(df_actual["Fecha"])
            df_actual = df_actual.set_index("Fecha")
        else:
            df_actual = pd.DataFrame(columns=["Precio"])

        # Nuevo segmento
        data = data[["Fecha", "Precio"]].set_index("Fecha")

        # Combinar sin duplicados
        df_comb = pd.concat([df_actual, data])
        df_comb = df_comb[~df_comb.index.duplicated(keep="last")].sort_index()
        
        df_final = df_comb.reset_index().rename(columns={"index": "Fecha"})

        # Guardar original
        df_final.to_parquet(ruta, index=False)

    return df