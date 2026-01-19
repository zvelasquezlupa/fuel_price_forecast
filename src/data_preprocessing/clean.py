import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Renombrar columnas para estandarizar
    if "Fecha Precio" in df.columns:
        df = df.rename(columns={"Fecha Precio": "Fecha"})
    else:
        raise KeyError("No se encontró la columna 'Fecha Precio' en el archivo CSV.")

    if "Promedio de Pvp Diario CUBO €/litro" in df.columns:
        df = df.rename(columns={"Promedio de Pvp Diario CUBO €/litro": "Precio"})
    else:
        raise KeyError("No se encontró la columna 'Promedio de Pvp Diario CUBO €/litro' en el archivo CSV.")

    # Convertir fecha y establecer como índice
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    df = df.dropna(subset=["Fecha", "Provincia", "Producto"])

    # Normalizar valores numéricos
    df["Precio"] = (
        df["Precio"]
        .astype(str)
        .str.replace(",", ".")
        .astype(float)
    )

    return df