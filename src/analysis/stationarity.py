from statsmodels.tsa.stattools import adfuller, kpss

def adf_test(series):
    result = adfuller(series, autolag="AIC")
    return {"stat": result[0], "pvalue": result[1]}

def kpss_test(series):
    result = kpss(series, regression="c", nlags="auto")
    return {"stat": result[0], "pvalue": result[1]}

def is_stationary(adf, kpss):
    return adf["pvalue"] < 0.05 and kpss["pvalue"] > 0.05

def validate_stationarity(series):
    adf = adf_test(series)
    kpss = kpss_test(series)
    return is_stationary(adf, kpss), adf, kpss