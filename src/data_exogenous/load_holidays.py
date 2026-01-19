import pandas as pd
import holidays
from src.utils.province_subdiv_map import PROVINCIA_TO_SUBDIV

def get_festivos_provincia(provincia, fechas):
    subdiv = PROVINCIA_TO_SUBDIV.get(provincia)

    # Si no existe, usar solo festivos nacionales
    if subdiv:
        spain_holidays = holidays.Spain(subdiv=subdiv)
    else:
        spain_holidays = holidays.Spain()

    fechas = pd.to_datetime(fechas)

    festivos = [1 if f in spain_holidays else 0 for f in fechas]

    return pd.DataFrame({"Festivo": festivos}, index=fechas)

