"""Dependance FastAPI extrayant l'utilisateur courant depuis le cookie de session httpOnly."""
import jwt
from fastapi import HTTPException, Request

from app.auth.schemas import User
from app.auth.security import decode_session_token
from app.auth.store import get_user_store
from app.core.config import get_settings


def get_current_user(request: Request) -> User:
    settings = get_settings()
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifie")

    try:
        claims = decode_session_token(token)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Session expiree, reconnecte-toi") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Session invalide") from exc

    user = get_user_store().get_by_id(claims["sub"])
    if user is None:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")
    return user
