import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
import os
from src.service.loadRate import loadRate  # <--- NUEVA CLASE
from src.data_loader import getBret,get_Bret_for_dates
from src.service.loadHolidays import get_festivos_provincia

def predict_segment(provincia, producto):
    # --- Construir ruta del archivo ---
    BASE_PATH = "src/data/segmented"
    ruta = os.path.join(BASE_PATH, provincia, producto, "stationary.parquet")

    # --- Leer datos ---
    df = pd.read_parquet(ruta)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df = df.set_index("Fecha").sort_index()

    # Serie dependiente
    y = df["Precio"]

    # --- Cargar tipo de cambio desde la API ---
    loader = loadRate()
    tipo_cambio_df = loader.get_rate_for_dates(df.index)

    # --- Cargar precio del petróleo ---
    df_petroleo = get_Bret_for_dates(df.index)

    # --- Cargar festivos ---
    festivos_df = get_festivos_provincia(provincia, df.index)

    # --- Construir exógenas ---
    exog = pd.DataFrame(index=df.index)
    exog["TipoCambio"] = tipo_cambio_df["TipoCambio"]
    exog["Petroleo"] = df_petroleo["precio_brent"]
    exog["Festivo"] = festivos_df["Festivo"]

    # --- LIMPIEZA CRÍTICA ---
    # Reemplazar inf
    exog = exog.replace([float("inf"), float("-inf")], pd.NA)

    # Rellenar NaNs hacia adelante y atrás
    exog = exog.ffill().bfill()

    # Verificación final
    if exog.isna().sum().sum() > 0:
        raise ValueError("Todavía hay NaNs en exog después de la limpieza.")

    # --- Train/Test split ---
    train_size = int(len(y) * 0.8)
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
    exog_train = exog.iloc[:train_size]
    exog_test = exog.iloc[train_size:]

    # --- Modelo SARIMAX ---
    model = SARIMAX(
        y_train,
        exog=exog_train,
        order=(1,1,1),
        seasonal_order=(0,1,1,7)
    )
    results = model.fit()

    # --- Guardar modelo entrenado ---
    model_path = os.path.join(BASE_PATH, provincia, producto, "model.pkl")
    results.save(model_path)

    # --- Predicción ---
    pred = results.get_forecast(steps=len(y_test), exog=exog_test)
    pred_mean = pred.predicted_mean
    pred_ci = pred.conf_int()

    # --- Evaluación ---
    mae = mean_absolute_error(y_test, pred_mean)
    rmse = mean_squared_error(y_test, pred_mean) ** 0.5  # RMSE manual
    
    # --- Guardar resultados de predicción ---
    df_pred = pd.DataFrame({
        "Real": y_test,
        "Predicción": pred_mean,
        "Lower": pred_ci.iloc[:, 0],
        "Upper": pred_ci.iloc[:, 1]
    })
    df_pred.to_parquet(os.path.join(BASE_PATH, provincia, producto, "prediccion.parquet"))


    return y_test, pred_mean, pred_ci, mae, rmse