"""Agregat User : identite issue de la connexion Google OAuth + preferences (cle API Gemini)."""
from datetime import UTC, datetime
from uuid import uuid4

from pydantic import Field

from app.shared.base import CamelModel


class User(CamelModel):
    """
    Modele de stockage interne - NE JAMAIS serialiser directement dans une reponse HTTP :
    gemini_api_key_encrypted est un secret chiffre qui n'a rien a faire sur le reseau, meme
    chiffre. Utiliser PublicUser (cf to_public_user ci-dessous) pour toute reponse API.
    """

    id: str = Field(default_factory=lambda: f"user_{uuid4().hex[:8]}")
    email: str
    google_sub: str  # identifiant unique et stable cote Google (claim "sub" du id_token)
    display_name: str
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    # Cle API Gemini personnelle (cf app/auth/crypto.py) - chiffree au repos, jamais en clair.
    # gemini_api_key_hint est un apercu partiel sur ("AIza...xyz"), stocke en clair pour
    # affichage, sans jamais permettre de reconstituer la cle complete.
    gemini_api_key_encrypted: str | None = None
    gemini_api_key_hint: str | None = None


class PublicUser(CamelModel):
    """Seule forme de User exposee via l'API (cf /auth/me, /auth/me/gemini-key)."""

    id: str
    email: str
    display_name: str
    created_at: str
    gemini_api_key_configured: bool
    gemini_api_key_hint: str | None = None


def to_public_user(user: User) -> PublicUser:
    return PublicUser(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        created_at=user.created_at,
        gemini_api_key_configured=user.gemini_api_key_encrypted is not None,
        gemini_api_key_hint=user.gemini_api_key_hint,
    )
