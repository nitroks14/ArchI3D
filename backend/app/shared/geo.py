"""Utilitaires geometriques/geo lies a l'orientation du batiment."""
CARDINAL_DIRECTIONS: list[str] = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def cardinal_from_azimuth(azimuth_deg: float) -> str:
    """Convertit un azimut (0-360, 0=Nord, sens horaire) en point cardinal a 8 directions."""
    normalized = azimuth_deg % 360
    index = round(normalized / 45) % 8
    return CARDINAL_DIRECTIONS[index]


def wall_azimuth_deg(local_angle_deg: float, building_north_offset_deg: float) -> float:
    """
    Azimut reel d'une facade = angle de la facade dans le repere du plan + decalage Nord du
    batiment (north_offset_deg). Utilise des que la vectorisation par facade (V2) fournit
    local_angle_deg pour chaque paroi individuelle (non disponible avec l'heuristique V1
    actuelle, qui agrege tout le perimetre d'une piece en une seule paroi "exterior").
    """
    return (local_angle_deg + building_north_offset_deg) % 360
