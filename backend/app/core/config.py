"""
Configuration centralisee de l'application, lue depuis les variables d'environnement.
Voir .env.example pour la liste complete des variables disponibles.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # --- Server ---
    cors_origins: str = "http://localhost:5173"
    storage_dir: str = "./storage"

    # --- AI provider ---
    ai_provider: str = "gemini"  # "gemini" | "claude"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5"

    # --- Storage backend ---
    storage_backend: str = "local"  # "local" | "r2"
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "archi3d-uploads"
    r2_public_base_url: str = ""

    # --- Authentification Google OAuth (cf app/auth) ---
    google_client_id: str = ""
    google_client_secret: str = ""
    # Doit correspondre EXACTEMENT a l'URI de redirection autorisee dans Google Cloud Console
    # (APIs & Services > Identifiants > le client OAuth) - cf README > Authentification.
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    # URL du frontend vers laquelle rediriger une fois la connexion Google reussie.
    frontend_url: str = "http://localhost:5173"

    # Secret de signature des sessions JWT (cookie httpOnly). A generer soi-meme, ex:
    # python -c "import secrets; print(secrets.token_urlsafe(48))" - ne JAMAIS commiter de valeur.
    session_secret: str = ""
    session_cookie_name: str = "archi3d_session"
    session_max_age_seconds: int = 60 * 60 * 24 * 7  # 7 jours

    # En local (frontend et backend sur des ports differents de localhost, meme "site"), les
    # valeurs par defaut ci-dessous fonctionnent. En production, le frontend (GitHub Pages) et
    # le backend (Render/Fly.io/...) sont sur des domaines differents (cross-site) : il faut alors
    # SESSION_COOKIE_SAMESITE=none ET SESSION_COOKIE_SECURE=true (obligatoire ensemble, sinon le
    # navigateur rejette le cookie) - cf README > Authentification > deploiement.
    session_cookie_secure: bool = False
    session_cookie_samesite: str = "lax"  # "lax" | "none" | "strict"

    # Cle de chiffrement symetrique (Fernet) utilisee pour stocker en base la cle API Gemini
    # personnelle de chaque utilisateur (jamais en clair). Generer avec :
    # python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    secrets_encryption_key: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def storage_path(self) -> Path:
        path = Path(self.storage_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
