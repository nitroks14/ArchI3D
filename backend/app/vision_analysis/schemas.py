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


class AerialImageAnalysisResult(CamelModel):
    roof_shape: str | None = None
    solar_panels_detected: bool = False
    solar_panels_area_estimate_m2: float | None = None
    solar_panels_location_hint: str | None = None
    confidence: str = "faible"
