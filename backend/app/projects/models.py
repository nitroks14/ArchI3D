"""
Etat persistant d'un projet ArchI3D : fichiers uploades, modele de batiment genere,
findings vision IA, reponses au questionnaire, dernier rapport thermique calcule.

Persiste en JSON sur disque (storage/{project_id}/state.json) - un choix volontairement
simple pour ce scaffolding V1 (pas de base de donnees). Voir README > roadmap V2.
"""
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import Field

from app.annexes.schemas import Annex
from app.shared.base import CamelModel
from app.shared.schemas import BuildingModel


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


class UploadedFile(CamelModel):
    id: str
    storage_key: str
    url: str
    filename: str
    content_type: str


class PlanFile(UploadedFile):
    floor_label: str = "RDC"


class PhotoFile(UploadedFile):
    kind: Literal["interior", "exterior"] = "interior"
    room_id: str | None = None
    analysis: dict | None = None  # dernier resultat d'analyse vision IA
    # Cap boussole (0-360, 0=Nord) releve au moment de la prise de vue via l'ecran camera integre
    # du frontend (cf presentation/components/CameraCapture). Absent pour les photos importees
    # autrement (upload classique, desktop sans capteur...) - toujours optionnel.
    compass_heading_deg: float | None = None


class MaterialInvoiceFile(UploadedFile):
    ocr_text: str = ""
    extracted: dict | None = None  # {material, product_reference, thickness_cm, r_value, quantity}
    linked_room_id: str | None = None
    linked_wall_id: str | None = None


class ProjectState(CamelModel):
    id: str = Field(default_factory=lambda: _new_id("project"))
    owner_id: str  # id du User proprietaire (cf app/auth) - tous les endpoints verifient ce champ
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    aerial_image: UploadedFile | None = None
    plans: list[PlanFile] = Field(default_factory=list)
    photos: list[PhotoFile] = Field(default_factory=list)
    invoices: list[MaterialInvoiceFile] = Field(default_factory=list)
    building_model: BuildingModel | None = None
    annexes: list[Annex] = Field(default_factory=list)
    questionnaire_answers: dict[str, str] = Field(default_factory=dict)
    thermal_report: dict | None = None
    aerial_image_analysis: dict | None = None  # dernier resultat d'analyse vision IA (toiture, solaire)
