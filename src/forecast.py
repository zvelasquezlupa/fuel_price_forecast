import os
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAXResults
from src.service.loadRate import loadRate
from src.data_loader import getBret,get_Bret_for_dates
from src.service.loadHolidays import get_festivos_provincia

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


def predict_future_days(provincia, producto, dias):
    # --- Cargar modelo ---
    results = load_model(provincia, producto)

    # --- Cargar histórico ---
    df_hist = load_historico(provincia, producto)
    last_date = df_hist.index.max()
    fechas_futuras = pd.date_range(start=last_date + pd.Timedelta(days=1),
                                   periods=dias, freq="D")
    
    print("Fechas Futuras:", fechas_futuras)


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

    pred_mean.index = exog.index
    pred_ci.index = exog.index

    df_pred = pd.DataFrame({
        "Predicción": pred_mean,
        "Lower": pred_ci.iloc[:, 0],
        "Upper": pred_ci.iloc[:, 1]
    })

    # --- Métricas del modelo ---
    metrics = {
        "AIC": results.aic,
        "BIC": results.bic,
        "LogLik": results.llf
    }

    return df_hist, df_pred, metrics