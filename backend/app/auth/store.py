"""
Persistance simple des utilisateurs en JSON sur disque (un seul fichier, storage/_users/users.json)
- coherent avec le choix V1 "pas de base de donnees" deja assume pour les projets (cf
app/projects/store.py et README > compromis). A remplacer par une vraie base des que le
multi-utilisateur reel devient un besoin de production.
"""
import json
from functools import lru_cache
from pathlib import Path

from app.auth.schemas import User
from app.core.config import get_settings


class UserStore:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text("{}")

    def _read_all(self) -> dict[str, dict]:
        return json.loads(self.file_path.read_text())

    def _write_all(self, data: dict[str, dict]) -> None:
        self.file_path.write_text(json.dumps(data, indent=2))

    def get_by_id(self, user_id: str) -> User | None:
        raw = self._read_all().get(user_id)
        return User.model_validate(raw) if raw else None

    def get_by_google_sub(self, google_sub: str) -> User | None:
        for raw in self._read_all().values():
            if raw.get("googleSub") == google_sub:
                return User.model_validate(raw)
        return None

    def save(self, user: User) -> None:
        data = self._read_all()
        data[user.id] = user.model_dump(by_alias=True)
        self._write_all(data)


@lru_cache
def get_user_store() -> UserStore:
    return UserStore(file_path=get_settings().storage_path / "_users" / "users.json")
