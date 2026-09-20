"""
Configuration centralisee de l'application, lue depuis les variables d'environnement.
Voir .env.example pour la liste complete des variables disponibles.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

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
