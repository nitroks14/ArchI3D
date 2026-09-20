"""Persistance simple des ProjectState en JSON sur disque, un fichier par projet."""
import json
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings
from app.projects.models import ProjectState
from app.storage.factory import get_storage_backend


class ProjectStore:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _state_path(self, project_id: str) -> Path:
        return self.root_dir / project_id / "state.json"

    def create(self, owner_id: str) -> ProjectState:
        state = ProjectState(owner_id=owner_id)
        # Arborescence de stockage {owner_id}/{project_id}/{plans,photos,aerial,invoices,model}
        # creee des la creation du projet (cf app/storage/base.py > ensure_project_structure).
        get_storage_backend().ensure_project_structure(owner_id, state.id)
        self.save(state)
        return state

    def get(self, project_id: str) -> ProjectState:
        path = self._state_path(project_id)
        if not path.exists():
            raise FileNotFoundError(f"Projet introuvable : {project_id}")
        return ProjectState.model_validate(json.loads(path.read_text()))

    def list_by_owner(self, owner_id: str) -> list[ProjectState]:
        """Scan simple du repertoire de stockage - suffisant pour le volume attendu en V1
        (pas de base de donnees, cf README > compromis). A indexer proprement en V2."""
        projects = []
        for state_path in self.root_dir.glob("*/state.json"):
            state = ProjectState.model_validate(json.loads(state_path.read_text()))
            if state.owner_id == owner_id:
                projects.append(state)
        return sorted(projects, key=lambda p: p.created_at, reverse=True)

    def save(self, state: ProjectState) -> None:
        path = self._state_path(state.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(state.model_dump_json(indent=2))


@lru_cache
def get_project_store() -> ProjectStore:
    return ProjectStore(root_dir=get_settings().storage_path / "_projects")
