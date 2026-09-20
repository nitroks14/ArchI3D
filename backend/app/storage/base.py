"""
Abstraction de stockage de fichiers binaires (photos, plans, factures materiaux, export GLB).

V1 propose deux implementations concretes :
- LocalDiskStorage : ecrit sur le disque du conteneur backend, servi via /files (defaut, aucune dependance externe)
- R2Storage : Cloudflare R2 (API compatible S3, tier gratuit jusqu'a 10 Go)

Le choix se fait via la variable d'environnement STORAGE_BACKEND.

Convention de cles partagee par tout le backend : {owner_id}/{project_id}/{category}/{filename},
avec category in PROJECT_SUBFOLDERS. Voir build_project_key ci-dessous - a utiliser partout plutot
que de construire les chemins a la main, pour eviter toute divergence entre modules.
"""
from abc import ABC, abstractmethod

# Sous-dossiers crees automatiquement a la creation d'un projet (cf ensure_project_structure).
PROJECT_SUBFOLDERS = ("plans", "photos", "aerial", "invoices", "model")


def build_project_key(owner_id: str, project_id: str, category: str, filename: str = "") -> str:
    """Construit une cle de stockage coherente {owner_id}/{project_id}/{category}[/{filename}]."""
    base = f"{owner_id}/{project_id}/{category}"
    return f"{base}/{filename}" if filename else base


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

    def ensure_project_structure(self, owner_id: str, project_id: str) -> None:
        """
        Cree a l'avance l'arborescence de dossiers d'un projet (plans/photos/aerial/invoices/model).
        No-op par defaut : un stockage objet (S3/R2) n'a pas de vraie notion de dossier vide, le
        prefixe emerge naturellement au premier upload. Seul LocalDiskStorage la redefinit pour
        creer reellement les repertoires sur disque.
        """
        return None
