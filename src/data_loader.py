import pandas as pd
from datetime import datetime
from src.persistence.file_store import save_parquet
from pathlib import Path

base_path = f"src/data/metadata"

def getBret():
    parquet_path = Path(base_path)
    if not parquet_path.exists():
            print(f"❌ Ruta no existe: {parquet_path.resolve()}")
            return None

    parquet_files = sorted(
        parquet_path.glob("precios_base_*.parquet"),
        reverse=True
    )

    if not parquet_files:
        print("❌ No se encontraron archivos parquet")
        return None
    
    return pd.read_parquet(parquet_files[0])

def get_Bret_for_dates(fechas):
    df_petroleo = getBret()

    # Normalizar columnas
    df_petroleo.columns = df_petroleo.columns.str.strip().str.lower()
    df_petroleo = df_petroleo.rename(columns={"fecha": "Fecha"})
    df_petroleo["Fecha"] = pd.to_datetime(df_petroleo["Fecha"])

    df_petroleo = df_petroleo.set_index("Fecha").sort_index()

    fechas = pd.to_datetime(fechas)
    df_fechas = pd.DataFrame(index=fechas)

    # Unir con el dataset de petróleo
    merged = df_fechas.join(df_petroleo, how="left")

    # Rellenar huecos
    merged = merged.ffill().bfill()

    return merged

def loadBret(uploaded_file):
    if uploaded_file is not None:
        # --- Data 1: Crude Oil (Brent) ---
        df_oil = pd.read_excel(
            uploaded_file,
            sheet_name="Data 1",
            skiprows=2
        )
        df_oil.columns = ["Fecha", "WTI", "Brent"]
        df_oil["Fecha"] = pd.to_datetime(df_oil["Fecha"])
        df_oil = df_oil.set_index("Fecha")

        # --- Data 2: Gasoline ---
        df_gas = pd.read_excel(
            uploaded_file,
            sheet_name="Data 2",
            skiprows=2
        )
        df_gas.columns = ["Fecha", "Gasoline_1", "Gasoline_2"]
        df_gas["Fecha"] = pd.to_datetime(df_gas["Fecha"])
        df_gas = df_gas.set_index("Fecha")

        df_gas = df_gas[["Gasoline_1"]].rename(
            columns={"Gasoline_1": "precio_gasolina"}
        )

        # --- Data 5: Diesel ---
        df_diesel = pd.read_excel(
            uploaded_file,
            sheet_name="Data 5",
            skiprows=2
        )
        df_diesel.columns = ["Fecha", "Diesel_1", "Diesel_2", "Diesel_3"]
        df_diesel["Fecha"] = pd.to_datetime(df_diesel["Fecha"])
        df_diesel = df_diesel.set_index("Fecha")

        df_diesel = df_diesel[["Diesel_1"]].rename(
            columns={"Diesel_1": "precio_diesel"}
        )

        # --- Unir todo ---
        df_final = (
            df_oil[["Brent"]]
            .rename(columns={"Brent": "precio_brent"})
            .join(df_gas, how="inner")
            .join(df_diesel, how="inner")
            .dropna()
            .reset_index()
        )

        # --- Guardar parquet con Fecha de carga ---
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parquet_name = f"precios_base_{timestamp}.parquet"

        df_final.to_parquet(parquet_name, index=False)
        
        save_parquet(df_final, base_path + "/" + parquet_name)

        return df_final