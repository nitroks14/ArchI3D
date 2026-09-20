"""
Endpoints d'ingestion : creation/liste de projets + upload direct (drag & drop cote frontend) des
fichiers sources. Pas d'integration Google Drive en V1 (cf README > roadmap V2).

Tous les endpoints qui operent sur un projet existant exigent d'etre authentifie ET proprietaire
du projet (cf app/projects/dependencies.get_owned_project_state) - 403 sinon.
"""
from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.auth.dependencies import get_current_user
from app.auth.schemas import User
from app.ingestion.service import store_invoice, store_photo, store_plan, store_upload
from app.projects.dependencies import get_owned_project_state
from app.projects.models import ProjectState
from app.projects.store import get_project_store

router = APIRouter(prefix="/projects", tags=["ingestion"])


@router.post("", response_model=ProjectState, status_code=201)
def create_project(current_user: User = Depends(get_current_user)) -> ProjectState:
    return get_project_store().create(owner_id=current_user.id)


@router.get("", response_model=list[ProjectState])
def list_projects(current_user: User = Depends(get_current_user)) -> list[ProjectState]:
    """Liste uniquement les projets du proprietaire courant (cf exigence controle d'acces)."""
    return get_project_store().list_by_owner(current_user.id)


@router.get("/{project_id}", response_model=ProjectState)
def get_project(state: ProjectState = Depends(get_owned_project_state)) -> ProjectState:
    return state


@router.post("/{project_id}/aerial-image", response_model=ProjectState)
async def upload_aerial_image(
    project_id: str, file: UploadFile = File(...), state: ProjectState = Depends(get_owned_project_state)
) -> ProjectState:
    store = get_project_store()
    state.aerial_image = await store_upload(state.owner_id, project_id, "aerial", file)
    store.save(state)
    return state


@router.post("/{project_id}/plans", response_model=ProjectState)
async def upload_plan(
    project_id: str,
    file: UploadFile = File(...),
    floor_label: str = Form("RDC"),
    state: ProjectState = Depends(get_owned_project_state),
) -> ProjectState:
    store = get_project_store()
    state.plans.append(await store_plan(state.owner_id, project_id, file, floor_label))
    store.save(state)
    return state


@router.post("/{project_id}/photos", response_model=ProjectState)
async def upload_photo(
    project_id: str,
    file: UploadFile = File(...),
    kind: str = Form("interior"),
    room_id: str | None = Form(None),
    # Cap boussole (0-360, 0=Nord) releve par l'ecran camera integre du frontend, si disponible.
    compass_heading_deg: float | None = Form(None),
    state: ProjectState = Depends(get_owned_project_state),
) -> ProjectState:
    store = get_project_store()
    state.photos.append(
        await store_photo(state.owner_id, project_id, file, kind, room_id, compass_heading_deg)
    )
    store.save(state)
    return state


@router.post("/{project_id}/invoices", response_model=ProjectState)
async def upload_invoice(
    project_id: str, file: UploadFile = File(...), state: ProjectState = Depends(get_owned_project_state)
) -> ProjectState:
    store = get_project_store()
    state.invoices.append(await store_invoice(state.owner_id, project_id, file))
    store.save(state)
    return state
