"""
Geocodage d'adresse et elevation, via des API publiques gratuites ne necessitant aucune cle :
- Nominatim (OpenStreetMap) pour lat/lon a partir d'une adresse texte
- Open-Meteo Elevation API pour l'altitude a partir de lat/lon

Nominatim impose un User-Agent identifiant l'application (politique d'usage) et une limite
d'1 requete/seconde - usage ponctuel ici (une geocodage par batiment), donc pas de souci de quota.
"""
import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
ELEVATION_URL = "https://api.open-meteo.com/v1/elevation"
USER_AGENT = "ArchI3D/0.1 (scaffolding - https://github.com/)"


class GeocodingError(RuntimeError):
    pass


def geocode_address(address: str) -> tuple[float, float]:
    response = httpx.get(
        NOMINATIM_URL,
        params={"q": address, "format": "json", "limit": 1},
        headers={"User-Agent": USER_AGENT},
        timeout=10.0,
    )
    response.raise_for_status()
    results = response.json()
    if not results:
        raise GeocodingError(f"Adresse introuvable : {address}")
    return float(results[0]["lat"]), float(results[0]["lon"])


def get_elevation(latitude: float, longitude: float) -> float | None:
    try:
        response = httpx.get(
            ELEVATION_URL, params={"latitude": latitude, "longitude": longitude}, timeout=10.0
        )
        response.raise_for_status()
        elevations = response.json().get("elevation", [])
        return float(elevations[0]) if elevations else None
    except Exception:
        # Non bloquant : l'altitude est une donnee secondaire, on continue sans elle si l'API echoue.
        return None
