"""
Dependance FastAPI partagee : charge un ProjectState par son id ET verifie que l'utilisateur
courant en est bien le proprietaire (403 sinon). A utiliser dans TOUS les routers qui operent
sur un projet existant, pour garantir un controle d'acces uniforme (cf README > Authentification).
"""
from fastapi import Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.schemas import User
from app.projects.models import ProjectState
from app.projects.store import get_project_store


def get_owned_project_state(project_id: str, current_user: User = Depends(get_current_user)) -> ProjectState:
    try:
        state = get_project_store().get(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if state.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Tu n'es pas proprietaire de ce projet")

    return state
