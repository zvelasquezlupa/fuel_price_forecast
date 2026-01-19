import os
import pandas as pd
import numpy as np
import json
from src.analysis.stationarity import adf_test, kpss_test, is_stationary, validate_stationarity
from src.analysis.transformations import difference
from src.utils.file_store import save_parquet, save_metadata

# Nuevas importaciones para análisis completo
from statsmodels.tsa.stattools import acf, pacf, grangercausalitytests
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy.stats import ttest_ind

from src.data_exogenous.load_rate import loadRate  # <--- NUEVA CLASE
from src.data_exogenous.load_bret import get_Bret_for_dates
from src.data_exogenous.load_holidays import get_festivos_provincia

def to_native(obj):
    if hasattr(obj, "item"):
        return obj.item()  # numpy → python
    return obj

def analisis_estacionaridad(provincia, producto):
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

    stationary_flag,adf, kpss  = validate_stationarity(serie)

    if stationary_flag:
        d_optimo = 0
        df_stationary = df[["Fecha", "Precio"]].copy()
    else:
        print("APLICANDO DIFERENCIACIÓN")
        precio_diff = serie.diff().dropna()
        es_est_diff,adf, kpss = validate_stationarity(precio_diff)
        
        if es_est_diff:
            d_optimo = 1
            df_stationary = precio_diff
        else:
            precio_diff2 = precio_diff.diff().dropna()
            es_est_diff,adf, kpss = validate_stationarity(precio_diff2)
            d_optimo = 2
            df_stationary = precio_diff2
            
        df_stationary = df_stationary.reset_index()

    save_parquet(df_stationary, stationary_path)

    # ✅ Conversión segura con to_native
    metadata = {
        "provincia": provincia,
        "producto": producto,
        "adf": {k: to_native(v) for k, v in adf.items()},
        "kpss": {k: to_native(v) for k, v in kpss.items()},
        "stationary": bool(stationary_flag), 
        "diferenciacion": d_optimo
    }

    save_metadata(metadata, metadata_path)


def get_analyze_complete(provincia, producto):
    base_path = f"src/data/segmented/{provincia}/{producto}/"
    original_path = base_path + "original.parquet"
    stationary_path = base_path + "stationary.parquet"
    metadata_path = base_path + "metadata.json"
    
    # Cargar datos con exógenas
    df_precio = pd.read_parquet(original_path)
    df_stationary = pd.read_parquet(stationary_path)
    df_precio['Fecha'] = pd.to_datetime(df_precio['Fecha'])
    df_precio = df_precio.set_index('Fecha').sort_index()
    
    # Cargar variables exógenas
    loader = loadRate()
    tipo_cambio_df = loader.get_rate_for_dates(df_precio.index)
    df_petroleo = get_Bret_for_dates(df_precio.index)
    festivos_df = get_festivos_provincia(provincia, df_precio.index)
    
    # Combinar
    df = pd.DataFrame(index=df_precio.index)
    df['Precio'] = df_precio['Precio']
    df['Brent'] = df_petroleo['precio_brent']
    df['TipoCambio'] = tipo_cambio_df['TipoCambio']
    df['Festivo'] = festivos_df['Festivo']
    df = df.replace([float("inf"), float("-inf")], pd.NA).ffill().bfill()
    
        # 3. Ejecutar análisis completo
    print("Calculando estadísticas...")
    metadata_completo = {
        "provincia": provincia,
        "producto": producto,
        "estadisticas": _calcular_estadisticas(df),
        "correlaciones": _analizar_correlaciones(df),
        "causalidad": _test_causalidad_granger(df),
        "multicolinealidad": _calcular_vif(df),
        "parametros_arima": _sugerir_parametros_arima(df['Precio']),
        "festivos_analisis": _analizar_festivos(df)
    }

    #

    metadata = pd.read_json(metadata_path)
    stationary_flag = bool(metadata["stationary"].iloc[0])
    print(stationary_flag, type(stationary_flag))

    return df, df_stationary, stationary_flag, metadata, metadata_completo



# ============================================================================
# FUNCIONES AUXILIARES DE ANÁLISIS
# ============================================================================

def _calcular_estadisticas(df):
    """Estadísticas descriptivas básicas"""
    stats = {
        'n_registros': int(len(df)),
        'periodo_inicio': df.index.min().strftime('%Y-%m-%d'),
        'periodo_fin': df.index.max().strftime('%Y-%m-%d'),
        'valores_nulos': {k: int(v) for k, v in df.isna().sum().to_dict().items()},
        'precio': {
            'media': float(df['Precio'].mean()),
            'std': float(df['Precio'].std()),
            'min': float(df['Precio'].min()),
            'max': float(df['Precio'].max()),
            'mediana': float(df['Precio'].median())
        },
        'brent': {
            'media': float(df['Brent'].mean()),
            'std': float(df['Brent'].std()),
            'min': float(df['Brent'].min()),
            'max': float(df['Brent'].max())
        },
        'festivos': {
            'total': int(df['Festivo'].sum()),
            'porcentaje': float(df['Festivo'].mean() * 100)
        }
    }
    return stats


def _analizar_correlaciones(df):
    """Análisis de correlaciones entre variables"""
    corr_matrix = df.corr()
    
    correlaciones = {
        'matriz': {col: {row: float(corr_matrix.loc[row, col]) 
                        for row in corr_matrix.index} 
                  for col in corr_matrix.columns},
        'precio_brent': float(corr_matrix.loc['Precio', 'Brent']),
        'precio_tipo_cambio': float(corr_matrix.loc['Precio', 'TipoCambio']),
        'precio_festivo': float(corr_matrix.loc['Precio', 'Festivo']),
        'interpretacion': {}
    }
    
    # Interpretación automática
    for var, col_name in [('Brent', 'precio_brent'), 
                          ('TipoCambio', 'precio_tipo_cambio'),
                          ('Festivo', 'precio_festivo')]:
        corr_val = correlaciones[col_name]
        abs_corr = abs(corr_val)
        
        if abs_corr > 0.7:
            fuerza = "MUY FUERTE"
        elif abs_corr > 0.4:
            fuerza = "MODERADA"
        else:
            fuerza = "DÉBIL"
        
        direccion = "POSITIVA" if corr_val > 0 else "NEGATIVA"
        correlaciones['interpretacion'][var] = {
            'descripcion': f"{fuerza} {direccion}",
            'valor': float(corr_val)
        }
    
    return correlaciones


def _test_causalidad_granger(df):
    """Test de Causalidad de Granger"""
    df_granger = df[['Precio', 'Brent', 'TipoCambio']].dropna()
    maxlag = min(14, len(df_granger) // 10)
    
    if maxlag < 1:
        return {'error': 'Datos insuficientes para test de Granger'}
    
    resultados = {}
    
    # Brent → Precio
    try:
        granger_brent = grangercausalitytests(
            df_granger[['Precio', 'Brent']], 
            maxlag=maxlag, 
            verbose=False
        )
        p_values = [granger_brent[lag][0]['ssr_ftest'][1] for lag in range(1, maxlag+1)]
        
        resultados['brent'] = {
            'causa_precio': bool(min(p_values) < 0.05),
            'p_value_minimo': float(min(p_values)),
            'lag_optimo': int(np.argmin(p_values) + 1)
        }
    except Exception as e:
        resultados['brent'] = {'error': str(e)}
    
    # TipoCambio → Precio
    try:
        granger_tc = grangercausalitytests(
            df_granger[['Precio', 'TipoCambio']], 
            maxlag=maxlag, 
            verbose=False
        )
        p_values = [granger_tc[lag][0]['ssr_ftest'][1] for lag in range(1, maxlag+1)]
        
        resultados['tipo_cambio'] = {
            'causa_precio': bool(min(p_values) < 0.05),
            'p_value_minimo': float(min(p_values)),
            'lag_optimo': int(np.argmin(p_values) + 1)
        }
    except Exception as e:
        resultados['tipo_cambio'] = {'error': str(e)}
    
    return resultados


def _calcular_vif(df):
    """Variance Inflation Factor (multicolinealidad)"""
    X = df[['Brent', 'TipoCambio', 'Festivo']].dropna()
    
    if len(X) < 10:
        return {'error': 'Datos insuficientes para calcular VIF'}
    
    vif_data = []
    for i, col in enumerate(X.columns):
        try:
            vif = variance_inflation_factor(X.values, i)
            vif_data.append({
                'variable': col,
                'vif': float(vif)
            })
        except:
            vif_data.append({
                'variable': col,
                'vif': None
            })
    
    vif_validos = [v['vif'] for v in vif_data if v['vif'] is not None]
    
    if not vif_validos:
        return {'error': 'No se pudo calcular VIF'}
    
    max_vif = max(vif_validos)
    
    if max_vif < 5:
        problema = "NO HAY PROBLEMAS"
    elif max_vif < 10:
        problema = "MODERADO"
    else:
        problema = "SEVERO"
    
    return {
        'vif_por_variable': vif_data,
        'vif_maximo': float(max_vif),
        'problema_multicolinealidad': problema
    }


def _sugerir_parametros_arima(serie, s=7):
    """
    Sugiere parámetros SARIMA basándose en ACF/PACF.
    Calcula p,d,q (no estacionales) y P,D,Q (estacionales).
    """

    serie_limpia = serie.dropna()

    if len(serie_limpia) < 50:
        return {'error': 'Serie muy corta para sugerir parámetros'}

    # ============================
    # 1. Determinar d (no estacional)
    # ============================
    try:
        adf = adf_test(serie_limpia)
        kpss = kpss_test(serie_limpia)
        stat = is_stationary(adf, kpss)

        if not stat:
            serie_diff = serie_limpia.diff().dropna()
            d = 1
        else:
            serie_diff = serie_limpia
            d = 0
    except:
        serie_diff = serie_limpia
        d = 0

    # ============================
    # 2. Calcular ACF y PACF para p y q
    # ============================
    nlags = min(20, len(serie_diff) // 3)
    acf_vals = acf(serie_diff, nlags=nlags)
    pacf_vals = pacf(serie_diff, nlags=nlags)

    umbral = 1.96 / np.sqrt(len(serie_diff))

    # p sugerido (PACF)
    significant_pacf = np.where(np.abs(pacf_vals[1:]) > umbral)[0]
    p_sugerido = min(significant_pacf[-1] + 1, 5) if len(significant_pacf) > 0 else 1

    # q sugerido (ACF)
    significant_acf = np.where(np.abs(acf_vals[1:]) > umbral)[0]
    q_sugerido = min(significant_acf[-1] + 1, 5) if len(significant_acf) > 0 else 1

    # ============================
    # 3. Determinar D (diferenciación estacional)
    # ============================
    try:
        serie_seasonal_diff = serie_limpia.diff(s).dropna()
        adf_s = adf_test(serie_seasonal_diff)
        kpss_s = kpss_test(serie_seasonal_diff)
        stat_s = is_stationary(adf_s, kpss_s)
        D = 1 if not stat_s else 0
    except:
        D = 1

    # ============================
    # 4. Calcular P y Q usando lags estacionales
    # ============================
    # Recalcular ACF/PACF sobre la serie diferenciada estacionalmente
    try:
        serie_seasonal = serie_limpia.diff(s).dropna()
        acf_s_vals = acf(serie_seasonal, nlags=s*3)
        pacf_s_vals = pacf(serie_seasonal, nlags=s*3)
    except:
        acf_s_vals = acf_vals
        pacf_s_vals = pacf_vals

    # P sugerido (PACF en lags s, 2s, 3s)
    P = 0
    for lag in [s, 2*s, 3*s]:
        if lag < len(pacf_s_vals) and abs(pacf_s_vals[lag]) > umbral:
            P += 1

    # Q sugerido (ACF en lags s, 2s, 3s)
    Q = 0
    for lag in [s, 2*s, 3*s]:
        if lag < len(acf_s_vals) and abs(acf_s_vals[lag]) > umbral:
            Q += 1

    # Limitar valores para evitar modelos explosivos
    P = min(P, 2)
    Q = min(Q, 2)

    # ============================
    # 5. Resultado final
    # ============================
    return {
        'p': int(p_sugerido),
        'd': int(d),
        'q': int(q_sugerido),
        'seasonal': {
            'P': int(P),
            'D': int(D),
            'Q': int(Q),
            's': int(s)
        },
        'recomendacion': f"SARIMAX({p_sugerido},{d},{q_sugerido})({P},{D},{Q},{s})",
        'acf_values': [float(v) for v in acf_vals[:min(11, len(acf_vals))]],
        'pacf_values': [float(v) for v in pacf_vals[:min(11, len(pacf_vals))]]
    }


def _analizar_festivos(df):
    """Análisis específico de festivos"""
    festivos = df[df['Festivo'] == 1]['Precio'].dropna()
    no_festivos = df[df['Festivo'] == 0]['Precio'].dropna()
    
    if len(festivos) < 2 or len(no_festivos) < 2:
        return {'error': 'Datos insuficientes para analizar festivos'}
    
    try:
        # Test t
        t_stat, p_value = ttest_ind(festivos, no_festivos)
        
        return {
            'n_festivos': int(len(festivos)),
            'n_no_festivos': int(len(no_festivos)),
            'media_festivos': float(festivos.mean()),
            'media_no_festivos': float(no_festivos.mean()),
            'diferencia': float(festivos.mean() - no_festivos.mean()),
            'test_t': {
                'estadistico': float(t_stat),
                'p_value': float(p_value),
                'diferencia_significativa': bool(p_value < 0.05)
            }
        }
    except Exception as e:
        return {'error': f'Error en test de festivos: {str(e)}'}
