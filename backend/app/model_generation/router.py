from fastapi import APIRouter, HTTPException

from app.shared.base import CamelModel

from app.model_generation.service import generate_building_model
from app.projects.store import get_project_store
from app.shared.schemas import BuildingModel

router = APIRouter(prefix="/projects", tags=["model-generation"])


class GenerateModelRequest(CamelModel):
    plan_id: str
    floor_label: str = "RDC"
    floor_level: int = 0
    meters_per_pixel: float = 0.02  # a defaut d'echelle detectee automatiquement (V2)
    default_ceiling_height_m: float = 2.5


@router.post("/{project_id}/model/generate", response_model=BuildingModel)
def generate_model(project_id: str, payload: GenerateModelRequest) -> BuildingModel:
    store = get_project_store()
    try:
        state = store.get(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        building = generate_building_model(
            state,
            plan_id=payload.plan_id,
            floor_label=payload.floor_label,
            floor_level=payload.floor_level,
            meters_per_pixel=payload.meters_per_pixel,
            default_ceiling_height_m=payload.default_ceiling_height_m,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    state.building_model = building
    store.save(state)
    return building


@router.get("/{project_id}/model", response_model=BuildingModel)
def get_model(project_id: str) -> BuildingModel:
    try:
        state = get_project_store().get(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if state.building_model is None:
        raise HTTPException(status_code=404, detail="Aucun modele genere pour ce projet")
    return state.building_model
