"""
Agregat Annex : structure secondaire sur la parcelle (abri de jardin, garage, dependance...),
distincte du Building principal. Geometrie simplifiee positionnee dans le meme repere local
(metres) que les pieces du batiment, ce qui permet de l'inserer directement a cote du batiment
dans le jumeau numerique 3D (cf app/model_generation/glb_export.py). Le Building reste l'unique
ancrage geolocalise (latitude/longitude) de la scene - la position de chaque annexe est exprimee
en offset (metres) par rapport a ce meme repere, pas via un geocodage independant (V1).
"""
from typing import Literal
from uuid import uuid4

from pydantic import Field

from app.shared.base import CamelModel
from app.shared.schemas import ConstructionTypeId, Wall

AnnexType = Literal["garden_shed", "garage", "outbuilding", "other"]


class Annex(CamelModel):
    id: str = Field(default_factory=lambda: f"annex_{uuid4().hex[:8]}")
    project_id: str
    type: AnnexType = "other"
    label: str = "Annexe"

    # Position/geometrie simplifiee dans le repere local du plan de masse (metres), coherent
    # avec RoomBoundingBox. Definie manuellement par l'utilisateur en V1 (flux "ajouter une
    # annexe sur le plan de masse") - detection automatique depuis l'image aerienne prevue en V2
    # (cf app/vision_analysis, meme principe que la detection des panneaux solaires).
    offset_x_m: float = 0.0
    offset_y_m: float = 0.0
    width_m: float = 3.0
    depth_m: float = 3.0
    height_m: float = 2.5
    rotation_deg: float = 0.0

    # Enveloppe thermique minimale, uniquement si l'annexe est chauffee/isolee. Sinon, seule la
    # geometrie compte (plan de masse + potentiel solaire de sa toiture, cf SolarInstallation).
    is_conditioned: bool = False
    construction_type: ConstructionTypeId = "unknown"
    walls: list[Wall] = Field(default_factory=list)

    source: Literal["user_input", "vision_estimate"] = "user_input"
