from fastapi import APIRouter, HTTPException

from app.projects.store import get_project_store
from app.thermal_engine.reference_data_loader import load_construction_types
from app.thermal_engine.service import compute_thermal_report

router = APIRouter(tags=["thermal-engine"])


@router.get("/reference/construction-types")
def get_construction_types() -> dict:
    """
    Catalogue illustre des typologies de construction courantes (ossature bois, ITE, monomur,
    parpaing+ITI, brique, pierre). Utilise par le questionnaire pour l'identification visuelle
    et comme reference de comparaison pour l'analyse vision IA. Images accessibles sous
    /files/reference/construction-types/{image_asset} (voir mount statique dans main.py).
    """
    return load_construction_types()


@router.get("/projects/{project_id}/thermal-report")
def get_thermal_report(project_id: str) -> dict:
    store = get_project_store()
    try:
        state = store.get(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if state.building_model is None:
        raise HTTPException(status_code=400, detail="Genere d'abord le modele 3D du batiment")

    report = compute_thermal_report(state.building_model)
    state.thermal_report = report
    store.save(state)
    return report
