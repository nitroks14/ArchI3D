from pathlib import Path

from app.storage.base import StorageBackend


class LocalDiskStorage(StorageBackend):
    """Stockage sur disque local, servi par FastAPI via le point de montage /files (voir main.py)."""

    def __init__(self, root_dir: Path, public_base_path: str = "/files"):
        self.root_dir = root_dir
        self.public_base_path = public_base_path.rstrip("/")

    def _resolve(self, key: str) -> Path:
        path = (self.root_dir / key).resolve()
        if self.root_dir.resolve() not in path.parents and path != self.root_dir.resolve():
            raise ValueError("Chemin de stockage invalide")
        return path

    def save(self, key: str, data: bytes, content_type: str) -> str:
        path = self._resolve(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return f"{self.public_base_path}/{key}"

    def read(self, key: str) -> bytes:
        return self._resolve(key).read_bytes()

    def delete(self, key: str) -> None:
        path = self._resolve(key)
        if path.exists():
            path.unlink()
