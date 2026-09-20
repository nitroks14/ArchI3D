"""
Abstraction de stockage de fichiers binaires (photos, plans, factures materiaux).

V1 propose deux implementations concretes :
- LocalDiskStorage : ecrit sur le disque du conteneur backend, servi via /files (defaut, aucune dependance externe)
- R2Storage : Cloudflare R2 (API compatible S3, tier gratuit jusqu'a 10 Go)

Le choix se fait via la variable d'environnement STORAGE_BACKEND.
"""
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes, content_type: str) -> str:
        """Enregistre le fichier et retourne une URL utilisable par le frontend."""

    @abstractmethod
    def read(self, key: str) -> bytes:
        """Relit le contenu binaire d'un fichier prealablement enregistre."""

    @abstractmethod
    def delete(self, key: str) -> None:
        ...
