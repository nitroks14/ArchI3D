"""
Schemas de sortie de l'analyse vision IA. Le provider IA (Gemini/Claude) renvoie un JSON libre
guide par le prompt (cle en snake_case, cf service.py) - on le valide ici via CamelModel
(populate_by_name=True) pour a la fois tolerer les champs manquants/superflus et garantir que la
reponse HTTP est bien serialisee en camelCase, coherent avec le reste de l'API et les types
TypeScript du frontend (src/domain/model/Project.ts).
"""
from app.shared.base import CamelModel


class PhotoAnalysisResult(CamelModel):
    materials: list[str] = []
    opening_types: list[str] = []
    apparent_insulation_state: str = "indeterminee"
    equipment: list[str] = []
    suggested_room_type: str | None = None
    suggested_room_name: str | None = None
    confidence: str = "faible"
    # Point d'integration : si la photo porte un cap boussole (PhotoFile.compass_heading_deg,
    # releve par l'ecran camera integre du frontend), il est transmis en indice au provider IA
    # (cf service.py) qui peut alors corroborer/suggerer l'orientation cardinale de la facade
    # photographiee. Non rattache automatiquement a une Wall specifique en V1 (les photos ne sont
    # pas encore associees a une paroi precise, seulement a une piece) - affinage V2.
    suggested_cardinal_orientation: str | None = None
    # Indice QUALITATIF pour la classe d'inertie thermique (cf app/thermal_engine/inertia.py) -
    # ex: ["cheminee en pierre", "chape beton apparente"]. Facteur secondaire non norme, distinct
    # du calcul structurel officiel base sur les parois.
    heavy_thermal_mass_elements_detected: list[str] = []


class AerialImageAnalysisResult(CamelModel):
    roof_shape: str | None = None
    solar_panels_detected: bool = False
    solar_panels_area_estimate_m2: float | None = None
    solar_panels_location_hint: str | None = None
    confidence: str = "faible"
