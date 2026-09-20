from functools import lru_cache

from app.climate.base import ClimateDataProvider


@lru_cache
def get_climate_data_provider() -> ClimateDataProvider:
    from app.climate.open_meteo_provider import OpenMeteoProvider

    return OpenMeteoProvider()
