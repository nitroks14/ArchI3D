"""Tests des sessions JWT - purement unitaires, aucun appel reseau/Google."""
import jwt
import pytest

from app.auth.schemas import User
from app.auth.security import create_session_token, decode_session_token
from app.core.config import get_settings


@pytest.fixture(autouse=True)
def _session_secret(monkeypatch):
    """Patche le secret de session sur l'instance Settings deja mise en cache, pour toute la
    duree du test, puis force la reconstruction d'une instance fraiche apres (isolation)."""
    settings = get_settings()
    monkeypatch.setattr(settings, "session_secret", "test-secret-not-for-prod")
    yield
    get_settings.cache_clear()


def _make_user() -> User:
    return User(email="jane@example.com", google_sub="google-sub-123", display_name="Jane Doe")


def test_create_and_decode_session_token_round_trip():
    user = _make_user()
    token = create_session_token(user)
    claims = decode_session_token(token)
    assert claims["sub"] == user.id
    assert claims["email"] == user.email


def test_decode_session_token_rejects_tampered_signature():
    user = _make_user()
    token = create_session_token(user)
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    with pytest.raises(jwt.InvalidTokenError):
        decode_session_token(tampered)


def test_decode_session_token_rejects_expired_token(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "session_max_age_seconds", -1)  # deja expire a la creation
    user = _make_user()
    token = create_session_token(user)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_session_token(token)
