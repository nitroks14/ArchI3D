from fastapi import APIRouter, Depends, HTTPException

from app.projects.dependencies import get_owned_project_state
from app.projects.models import ProjectState
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
def get_thermal_report(state: ProjectState = Depends(get_owned_project_state)) -> dict:
    if state.building_model is None:
        raise HTTPException(status_code=400, detail="Genere d'abord le modele 3D du batiment")

    # Facteur secondaire qualitatif d'inertie (mobilier/elements massifs) - cf app/thermal_engine
    # /inertia.py pour la distinction avec le facteur structurel norme.
    heavy_mass_hint = state.questionnaire_answers.get("building:heavy_thermal_mass")
    heavy_mass_vision_hints = [
        item
        for photo in state.photos
        if photo.analysis
        for item in photo.analysis.get("heavyThermalMassElementsDetected", [])
    ]

    report = compute_thermal_report(state.building_model, heavy_mass_hint, heavy_mass_vision_hints)
    state.thermal_report = report
    get_project_store().save(state)
    return report
