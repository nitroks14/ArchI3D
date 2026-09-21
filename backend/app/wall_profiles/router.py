"""
Endpoints de la bibliotheque de profils de parois reutilisables (cf schemas.py/service.py) :
- GET  /projects/{id}/wall-profiles                       -> liste des profils captures
- POST /projects/{id}/wall-profiles/{profile_id}/apply-to-unset -> action groupee EXPLICITE,
  jamais automatique (cf consigne produit) : applique un profil a toutes les parois du type
  donne qui n'ont encore aucune donnee, sans jamais ecraser une paroi deja renseignee.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.projects.dependencies import get_owned_project_state
from app.projects.models import ProjectState
from app.projects.store import get_project_store
from app.shared.base import CamelModel
from app.wall_profiles.schemas import WallAssemblyProfile
from app.wall_profiles.service import apply_profile_to_unset_walls

router = APIRouter(prefix="/projects/{project_id}/wall-profiles", tags=["wall-profiles"])


class ApplyProfileRequest(CamelModel):
    wall_kind: str = "exterior"


@router.get("", response_model=list[WallAssemblyProfile])
def list_wall_profiles(
    state: ProjectState = Depends(get_owned_project_state),
) -> list[WallAssemblyProfile]:
    return state.wall_assembly_profiles


@router.post("/{profile_id}/apply-to-unset")
def apply_profile_to_unset(
    profile_id: str,
    payload: ApplyProfileRequest,
    state: ProjectState = Depends(get_owned_project_state),
) -> dict:
    if state.building_model is None:
        raise HTTPException(status_code=400, detail="Aucun modele de batiment genere")

    try:
        applied_count = apply_profile_to_unset_walls(
            state.wall_assembly_profiles, state.building_model, profile_id, payload.wall_kind
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    get_project_store().save(state)
    return {"appliedCount": applied_count, "buildingModel": state.building_model.model_dump(by_alias=True)}
