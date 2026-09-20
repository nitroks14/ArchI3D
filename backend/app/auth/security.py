"""
Sessions JWT signees (HS256) posees en cookie httpOnly - pas de stockage du token Google lui
meme cote client, uniquement notre propre session applicative (cf consigne securite).
"""
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.auth.schemas import User
from app.core.config import get_settings

ALGORITHM = "HS256"


def create_session_token(user: User) -> str:
    settings = get_settings()
    if not settings.session_secret:
        raise RuntimeError(
            "SESSION_SECRET manquant. Genere une valeur aleatoire "
            "(python3 -c \"import secrets; print(secrets.token_urlsafe(48))\") "
            "et renseigne-la dans le fichier .env du backend."
        )
    now = datetime.now(UTC)
    payload = {
        "sub": user.id,
        "email": user.email,
        "iat": now,
        "exp": now + timedelta(seconds=settings.session_max_age_seconds),
    }
    return jwt.encode(payload, settings.session_secret, algorithm=ALGORITHM)


def decode_session_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    # leve jwt.ExpiredSignatureError / jwt.InvalidTokenError si invalide - a capter par l'appelant.
    return jwt.decode(token, settings.session_secret, algorithms=[ALGORITHM])
