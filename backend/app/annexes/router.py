"""
Endpoints de l'agregat Annex (abri de jardin, garage, dependance...) : creation/liste/mise a
jour/suppression, independants du Building principal. Chaque mutation regenere l'export GLB pour
que l'annexe apparaisse immediatement a cote du batiment dans le viewer 3D.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.annexes.schemas import Annex, AnnexType
from app.model_generation.service import regenerate_glb
from app.projects.dependencies import get_owned_project_state
from app.projects.models import ProjectState
from app.projects.store import get_project_store
from app.shared.base import CamelModel

router = APIRouter(prefix="/projects/{project_id}/annexes", tags=["annexes"])


class CreateAnnexRequest(CamelModel):
    type: AnnexType = "other"
    label: str = "Annexe"
    offset_x_m: float = 0.0
    offset_y_m: float = 0.0
    width_m: float = 3.0
    depth_m: float = 3.0
    height_m: float = 2.5
    rotation_deg: float = 0.0
    is_conditioned: bool = False


class UpdateAnnexRequest(CamelModel):
    label: str | None = None
    offset_x_m: float | None = None
    offset_y_m: float | None = None
    width_m: float | None = None
    depth_m: float | None = None
    height_m: float | None = None
    rotation_deg: float | None = None
    is_conditioned: bool | None = None


def _sync_glb(state: ProjectState) -> None:
    """Regenere l'export GLB si un modele de batiment existe deja pour ce projet."""
    if state.building_model is not None:
        state.building_model.glb_url = regenerate_glb(state, state.building_model, state.annexes)


@router.get("", response_model=list[Annex])
def list_annexes(state: ProjectState = Depends(get_owned_project_state)) -> list[Annex]:
    return state.annexes


@router.post("", response_model=Annex, status_code=201)
def create_annex(
    payload: CreateAnnexRequest, state: ProjectState = Depends(get_owned_project_state)
) -> Annex:
    annex = Annex(project_id=state.id, **payload.model_dump())
    state.annexes.append(annex)
    _sync_glb(state)
    get_project_store().save(state)
    return annex


@router.patch("/{annex_id}", response_model=Annex)
def update_annex(
    annex_id: str,
    payload: UpdateAnnexRequest,
    state: ProjectState = Depends(get_owned_project_state),
) -> Annex:
    annex = next((a for a in state.annexes if a.id == annex_id), None)
    if annex is None:
        raise HTTPException(status_code=404, detail="Annexe introuvable")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(annex, field, value)

    _sync_glb(state)
    get_project_store().save(state)
    return annex


@router.delete("/{annex_id}", status_code=204)
def delete_annex(annex_id: str, state: ProjectState = Depends(get_owned_project_state)) -> None:
    if not any(a.id == annex_id for a in state.annexes):
        raise HTTPException(status_code=404, detail="Annexe introuvable")
    state.annexes = [a for a in state.annexes if a.id != annex_id]

    _sync_glb(state)
    get_project_store().save(state)
