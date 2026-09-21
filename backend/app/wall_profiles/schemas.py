"""
Profil de paroi reutilisable (WallAssemblyProfile) : capitalise une composition de paroi deja
renseignee (type de construction + couches de materiaux) pour la reproposer automatiquement sur
les elements similaires du meme projet, plutot que de forcer une nouvelle saisie a chaque mur/
plancher/toiture. Scope V1 : rattache au PROJET (pas a l'utilisateur globalement) - plus simple
et plus sur (pas de fuite d'un profil entre deux maisons differentes). Cf app/wall_profiles/service.py.
"""
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import Field

from app.shared.base import CamelModel
from app.shared.schemas import ConstructionTypeId, MaterialLayer, MaterialSource


class WallAssemblyProfile(CamelModel):
    id: str = Field(default_factory=lambda: f"profile_{uuid4().hex[:8]}")
    label: str
    applicable_wall_kind: Literal["exterior", "interior", "floor", "roof"] = "exterior"
    construction_type: ConstructionTypeId = "unknown"
    layers: list[MaterialLayer] = Field(default_factory=list)
    source: MaterialSource = "user_input"
    usage_count: int = 1
    last_used_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
