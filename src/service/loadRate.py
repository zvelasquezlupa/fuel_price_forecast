import pandas as pd
import requests
from io import StringIO

class loadRate:
    """
    Clase para cargar el tipo de cambio EUR→USD desde la API del Banco Central Europeo.
    """

    URL = "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?format=csvdata"

    def __init__(self):
        self.df = None

    def load(self):
        """Descarga y carga el CSV desde la API."""
        response = requests.get(self.URL)
        response.raise_for_status()

        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)

        # Normalizar columnas
        df["TIME_PERIOD"] = pd.to_datetime(df["TIME_PERIOD"])
        df = df.rename(columns={
            "TIME_PERIOD": "Fecha",
            "OBS_VALUE": "TipoCambio"
        })

        df = df.set_index("Fecha").sort_index()

        self.df = df
        return df

    def get_rate_for_dates(self, fechas):
        """
        Devuelve un DataFrame con el tipo de cambio alineado a las fechas solicitadas.
        Si no hay dato (fin de semana/festivo), se hace forward-fill.
        """
        if self.df is None:
            self.load()

        # Crear DataFrame base con las fechas del segmento
        fechas = pd.to_datetime(fechas)
        df_fechas = pd.DataFrame(index=fechas)

        # Unir con el tipo de cambio
        merged = df_fechas.join(self.df, how="left")

        # Rellenar huecos (ECB no publica fines de semana)
        merged["TipoCambio"] = merged["TipoCambio"].ffill().bfill()

        return merged