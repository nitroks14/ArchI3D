"""Persistance simple des ProjectState en JSON sur disque, un fichier par projet."""
import json
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings
from app.projects.models import ProjectState


class ProjectStore:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _state_path(self, project_id: str) -> Path:
        return self.root_dir / project_id / "state.json"

    def create(self) -> ProjectState:
        state = ProjectState()
        self.save(state)
        return state

    def get(self, project_id: str) -> ProjectState:
        path = self._state_path(project_id)
        if not path.exists():
            raise FileNotFoundError(f"Projet introuvable : {project_id}")
        return ProjectState.model_validate(json.loads(path.read_text()))

    def save(self, state: ProjectState) -> None:
        path = self._state_path(state.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(state.model_dump_json(indent=2))


@lru_cache
def get_project_store() -> ProjectStore:
    return ProjectStore(root_dir=get_settings().storage_path / "_projects")
