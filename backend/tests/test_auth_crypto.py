"""Tests du chiffrement des secrets utilisateur - purement unitaires, aucun appel reseau."""
import pytest
from cryptography.fernet import Fernet

from app.auth.crypto import decrypt_secret, encrypt_secret, mask_secret
from app.core.config import get_settings


@pytest.fixture(autouse=True)
def _encryption_key(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "secrets_encryption_key", Fernet.generate_key().decode())
    yield
    get_settings.cache_clear()


def test_encrypt_decrypt_round_trip():
    plaintext = "AIzaSyExampleFakeKeyNotReal12345"
    ciphertext = encrypt_secret(plaintext)
    assert ciphertext != plaintext
    assert decrypt_secret(ciphertext) == plaintext


def test_mask_secret_keeps_only_a_short_preview():
    masked = mask_secret("AIzaSyExampleFakeKeyNotReal12345")
    assert masked.startswith("AIza")
    assert masked.endswith("345")
    assert "ExampleFakeKeyNotReal" not in masked


def test_mask_secret_short_value_is_fully_hidden():
    assert mask_secret("short") == "****"
