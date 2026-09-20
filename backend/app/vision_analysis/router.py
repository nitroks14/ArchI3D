from fastapi import APIRouter, HTTPException

from app.projects.store import get_project_store
from app.storage.factory import get_storage_backend
from app.vision_analysis.service import analyze_photo

router = APIRouter(prefix="/projects", tags=["vision-analysis"])


@router.post("/{project_id}/photos/{photo_id}/analyze")
def analyze_project_photo(project_id: str, photo_id: str) -> dict:
    store = get_project_store()
    try:
        state = store.get(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    photo = next((p for p in state.photos if p.id == photo_id), None)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo introuvable")

    try:
        image_bytes = get_storage_backend().read(photo.storage_key)
        analysis = analyze_photo(image_bytes, photo.content_type)
    except RuntimeError as exc:
        # cle API du provider IA manquante : erreur explicite plutot qu'un 500 opaque
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    photo.analysis = analysis
    store.save(state)
    return analysis
