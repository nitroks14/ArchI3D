from functools import lru_cache

from app.core.config import get_settings
from app.storage.base import StorageBackend


@lru_cache
def get_storage_backend() -> StorageBackend:
    settings = get_settings()

    if settings.storage_backend == "r2":
        from app.storage.r2_storage import R2Storage

        return R2Storage(
            account_id=settings.r2_account_id,
            access_key_id=settings.r2_access_key_id,
            secret_access_key=settings.r2_secret_access_key,
            bucket_name=settings.r2_bucket_name,
            public_base_url=settings.r2_public_base_url,
        )

    from app.storage.local_storage import LocalDiskStorage

    return LocalDiskStorage(root_dir=settings.storage_path)
