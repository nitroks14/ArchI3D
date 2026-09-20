"""
Implementation basee sur l'API gratuite Open-Meteo (aucune cle requise) :
https://open-meteo.com/en/docs/historical-weather-api

Calcule un DJU (degres-jours unifies, base 18) approximatif a partir des temperatures
journalieres moyennes de la derniere annee complete disponible. Repli automatique sur une
constante nationale moyenne si l'appel reseau echoue (sandbox sans acces internet, quota
depasse, etc.) - le moteur thermique reste utilisable hors-ligne.
"""
import logging
from datetime import date, timedelta

import httpx

from app.climate.base import ClimateDataProvider, ClimateSummary

logger = logging.getLogger(__name__)

ARCHIVE_API_URL = "https://archive-api.open-meteo.com/v1/archive"
FALLBACK_DJU_BASE18 = 2200  # moyenne climat France, utilisee si l'API est indisponible
HEATING_BASE_TEMP_C = 18.0


class OpenMeteoProvider(ClimateDataProvider):
    def get_climate_summary(self, latitude: float, longitude: float) -> ClimateSummary:
        end = date.today() - timedelta(days=7)  # marge : les donnees tres recentes peuvent manquer
        start = end - timedelta(days=365)

        try:
            response = httpx.get(
                ARCHIVE_API_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                    "daily": "temperature_2m_mean",
                    "timezone": "auto",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            daily_temps = response.json()["daily"]["temperature_2m_mean"]
            valid_temps = [t for t in daily_temps if t is not None]
            if not valid_temps:
                raise ValueError("Reponse Open-Meteo sans donnees de temperature exploitables")

            dju = sum(max(0.0, HEATING_BASE_TEMP_C - t) for t in valid_temps)
            avg_temp = sum(valid_temps) / len(valid_temps)

            return ClimateSummary(
                latitude=latitude,
                longitude=longitude,
                estimated_dju_base18=round(dju, 0),
                average_annual_temperature_c=round(avg_temp, 1),
                data_source="open-meteo.com (historical weather, 365 derniers jours)",
            )
        except Exception as exc:
            logger.warning("Open-Meteo indisponible (%s) - repli sur DJU constant.", exc)
            return ClimateSummary(
                latitude=latitude,
                longitude=longitude,
                estimated_dju_base18=FALLBACK_DJU_BASE18,
                data_source="valeur par defaut (Open-Meteo indisponible)",
                notes=f"Erreur lors de l'appel a Open-Meteo : {exc}",
            )
