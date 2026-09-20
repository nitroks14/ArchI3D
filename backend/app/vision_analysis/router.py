from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.schemas import User
from app.projects.dependencies import get_owned_project_state
from app.projects.models import ProjectState
from app.projects.store import get_project_store
from app.shared.schemas import SolarInstallation
from app.storage.factory import get_storage_backend
from app.vision_analysis.schemas import AerialImageAnalysisResult, PhotoAnalysisResult
from app.vision_analysis.service import analyze_aerial_image, analyze_photo

router = APIRouter(prefix="/projects", tags=["vision-analysis"])


@router.post("/{project_id}/photos/{photo_id}/analyze", response_model=PhotoAnalysisResult)
def analyze_project_photo(
    photo_id: str,
    state: ProjectState = Depends(get_owned_project_state),
    current_user: User = Depends(get_current_user),
) -> PhotoAnalysisResult:
    photo = next((p for p in state.photos if p.id == photo_id), None)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo introuvable")

    try:
        image_bytes = get_storage_backend().read(photo.storage_key)
        analysis = analyze_photo(
            image_bytes, photo.content_type, current_user, photo.compass_heading_deg
        )
    except RuntimeError as exc:
        # cle API du provider IA manquante : erreur explicite plutot qu'un 500 opaque
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    photo.analysis = analysis.model_dump(by_alias=True)
    get_project_store().save(state)
    return analysis


@router.post("/{project_id}/aerial-image/analyze", response_model=AerialImageAnalysisResult)
def analyze_project_aerial_image(
    state: ProjectState = Depends(get_owned_project_state),
    current_user: User = Depends(get_current_user),
) -> AerialImageAnalysisResult:
    """
    Analyse l'image aerienne du projet : forme de toiture + detection/position approximative des
    panneaux solaires existants. Si des panneaux sont detectes et qu'un modele de batiment existe
    deja, une SolarInstallation (source="vision_estimate") est ajoutee automatiquement - a
    affiner ensuite par l'utilisateur (orientation/inclinaison precises, cf questionnaire V2).
    """
    if state.aerial_image is None:
        raise HTTPException(status_code=400, detail="Aucune image aerienne uploadee pour ce projet")

    try:
        image_bytes = get_storage_backend().read(state.aerial_image.storage_key)
        analysis = analyze_aerial_image(image_bytes, state.aerial_image.content_type, current_user)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    state.aerial_image_analysis = analysis.model_dump(by_alias=True)

    if analysis.solar_panels_detected and state.building_model is not None:
        state.building_model.solar_installations.append(
            SolarInstallation(
                source="vision_estimate",
                area_m2=analysis.solar_panels_area_estimate_m2,
            )
        )

    get_project_store().save(state)
    return analysis
