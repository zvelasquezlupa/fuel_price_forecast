import os
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAXResults
from src.data_exogenous.load_rate import loadRate
from src.data_exogenous.load_bret import get_Bret_for_dates
from src.data_exogenous.load_holidays import get_festivos_provincia

BASE_PATH = "src/data/segmented"
def load_model(provincia, producto):
    model_path = os.path.join(BASE_PATH, provincia, producto, "model.pkl")
    return SARIMAXResults.load(model_path)


def load_historico(provincia, producto):
    ruta = os.path.join(BASE_PATH, provincia, producto, "stationary.parquet")
    df = pd.read_parquet(ruta)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df = df.set_index("Fecha").sort_index()
    return df

def reintegrar_prediccion(pred_mean, pred_ci, ultimo_precio_real):
    precio_real = pred_mean.cumsum() + ultimo_precio_real
    lower_real = pred_ci.iloc[:, 0].cumsum() + ultimo_precio_real
    upper_real = pred_ci.iloc[:, 1].cumsum() + ultimo_precio_real

    return pd.DataFrame({
        "Predicción": precio_real,
        "Lower": lower_real,
        "Upper": upper_real
    })


def predict_future_days(provincia, producto, dias):
    # --- Cargar modelo ---
    model_path = os.path.join(BASE_PATH, provincia, producto, "model.pkl")
    results = SARIMAXResults.load(model_path)

    # --- Cargar histórico real ---
    ruta_original = os.path.join(BASE_PATH, provincia, producto, "original.parquet")
    df_original = pd.read_parquet(ruta_original)
    df_original["Fecha"] = pd.to_datetime(df_original["Fecha"])
    df_original = df_original.set_index("Fecha").sort_index()

    ultimo_precio_real = df_original["Precio"].iloc[-1]

    # --- Generar fechas futuras ---
    last_date = df_original.index.max()
    fechas_futuras = pd.date_range(start=last_date + pd.Timedelta(days=1),
                                   periods=dias, freq="D")

    # --- Exógenas futuras ---
    loader = loadRate()
    tipo_cambio_df = loader.get_rate_for_dates(fechas_futuras)
    df_petroleo = get_Bret_for_dates(fechas_futuras)
    festivos_df = get_festivos_provincia(provincia, fechas_futuras)

    exog = pd.DataFrame(index=fechas_futuras)
    exog["TipoCambio"] = tipo_cambio_df["TipoCambio"]
    exog["Petroleo"] = df_petroleo["precio_brent"]
    exog["Festivo"] = festivos_df["Festivo"]
    exog = exog.replace([float("inf"), float("-inf")], pd.NA).ffill().bfill()

    # --- Predicción ---
    pred = results.get_forecast(steps=len(exog), exog=exog)

    pred_mean = pred.predicted_mean
    pred_ci = pred.conf_int()

    # Forzar fechas correctas
    pred_mean.index = exog.index
    pred_ci.index = exog.index

    # --- Convertir a valores reales ---
    df_pred_real = reintegrar_prediccion(pred_mean, pred_ci, ultimo_precio_real)

    # --- Métricas del modelo ---
    metrics = {
        "AIC": results.aic,
        "BIC": results.bic,
        "LogLik": results.llf
    }

    return df_original, df_pred_real, metrics