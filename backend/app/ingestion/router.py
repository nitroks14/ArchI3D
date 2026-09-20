"""
Endpoints d'ingestion : creation de projet + upload direct (drag & drop cote frontend) des
fichiers sources. Pas d'integration Google Drive en V1 (cf README > roadmap V2).
"""
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.ingestion.service import store_invoice, store_photo, store_plan, store_upload
from app.projects.models import ProjectState
from app.projects.store import get_project_store

router = APIRouter(prefix="/projects", tags=["ingestion"])


@router.post("", response_model=ProjectState, status_code=201)
def create_project() -> ProjectState:
    return get_project_store().create()


@router.get("/{project_id}", response_model=ProjectState)
def get_project(project_id: str) -> ProjectState:
    try:
        return get_project_store().get(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{project_id}/aerial-image", response_model=ProjectState)
async def upload_aerial_image(project_id: str, file: UploadFile = File(...)) -> ProjectState:
    store = get_project_store()
    state = _get_or_404(project_id)
    state.aerial_image = await store_upload(project_id, "aerial", file)
    store.save(state)
    return state


@router.post("/{project_id}/plans", response_model=ProjectState)
async def upload_plan(
    project_id: str, file: UploadFile = File(...), floor_label: str = Form("RDC")
) -> ProjectState:
    store = get_project_store()
    state = _get_or_404(project_id)
    state.plans.append(await store_plan(project_id, file, floor_label))
    store.save(state)
    return state


@router.post("/{project_id}/photos", response_model=ProjectState)
async def upload_photo(
    project_id: str,
    file: UploadFile = File(...),
    kind: str = Form("interior"),
    room_id: str | None = Form(None),
) -> ProjectState:
    store = get_project_store()
    state = _get_or_404(project_id)
    state.photos.append(await store_photo(project_id, file, kind, room_id))
    store.save(state)
    return state


@router.post("/{project_id}/invoices", response_model=ProjectState)
async def upload_invoice(project_id: str, file: UploadFile = File(...)) -> ProjectState:
    store = get_project_store()
    state = _get_or_404(project_id)
    state.invoices.append(await store_invoice(project_id, file))
    store.save(state)
    return state


def _get_or_404(project_id: str):
    try:
        return get_project_store().get(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
