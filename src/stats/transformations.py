def difference(series, lag=1): #elimina tendencia
    series_sta=series.diff(lag)
    series_sta2=series_sta.diff(lag)
    series_stacionary=series_sta2[lag:-1]
    return series_stacionary

def seasonal_difference(series, season=7):
    return series.diff(season).dropna()