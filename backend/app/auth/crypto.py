"""
Chiffrement symetrique (Fernet/AES) des secrets utilisateur stockes en base - actuellement la
cle API Gemini personnelle de chaque User. Jamais stockee ni loggee en clair.
"""
import logging

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class SecretEncryptionError(RuntimeError):
    pass


def _fernet() -> Fernet:
    settings = get_settings()
    if not settings.secrets_encryption_key:
        raise SecretEncryptionError(
            "SECRETS_ENCRYPTION_KEY manquant. Genere une cle avec "
            "python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\" "
            "et renseigne-la dans le fichier .env du backend."
        )
    return Fernet(settings.secrets_encryption_key.encode())


def encrypt_secret(plaintext: str) -> str:
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt_secret(ciphertext: str) -> str:
    try:
        return _fernet().decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:
        # ne jamais inclure le contenu chiffre/dechiffre dans l'exception ou un log
        raise SecretEncryptionError("Dechiffrement impossible (cle de chiffrement changee ?)") from exc


def mask_secret(plaintext: str) -> str:
    """Apercu partiel sur, destine a etre affiche/stocke en clair (ex: 'AIza...xyz')."""
    if len(plaintext) <= 8:
        return "****"
    return f"{plaintext[:4]}...{plaintext[-3:]}"
