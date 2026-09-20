"""
Abstraction du fournisseur de donnees climatiques locales, utilisee (a terme) par le moteur
thermique pour remplacer la constante DJU_DEFAULT par une valeur derivee de la position
geographique reelle du batiment, et pour les futurs calculs d'apports solaires bioclimatiques.

V1 : une seule implementation concrete (OpenMeteoProvider, API gratuite sans cle). L'irradiation
solaire par orientation/inclinaison (PVGIS, JRC europeen, gratuit sans cle) n'est pas encore
appelee - point d'integration prevu ici en V2 (cf README > roadmap).
"""
from abc import ABC, abstractmethod
from pydantic import BaseModel


class ClimateSummary(BaseModel):
    latitude: float
    longitude: float
    estimated_dju_base18: float  # degres-jours unifies, base 18 - utilise par le moteur thermique
    average_annual_temperature_c: float | None = None
    data_source: str
    notes: str | None = None


class ClimateDataProvider(ABC):
    @abstractmethod
    def get_climate_summary(self, latitude: float, longitude: float) -> ClimateSummary:
        ...
