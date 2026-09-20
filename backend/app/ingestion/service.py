"""Sauvegarde des fichiers uploades (image aerienne, plans, photos, factures) via le storage backend."""
from uuid import uuid4

from fastapi import UploadFile

from app.projects.models import MaterialInvoiceFile, PhotoFile, PlanFile, UploadedFile
from app.storage.factory import get_storage_backend


def _storage_key(project_id: str, category: str, filename: str) -> str:
    safe_name = filename.replace("/", "_")
    return f"{project_id}/{category}/{uuid4().hex[:8]}_{safe_name}"


async def store_upload(project_id: str, category: str, file: UploadFile) -> UploadedFile:
    data = await file.read()
    key = _storage_key(project_id, category, file.filename or "upload.bin")
    url = get_storage_backend().save(key, data, file.content_type or "application/octet-stream")
    return UploadedFile(
        id=f"{category}_{uuid4().hex[:8]}",
        storage_key=key,
        url=url,
        filename=file.filename or "upload.bin",
        content_type=file.content_type or "application/octet-stream",
    )


async def store_plan(project_id: str, file: UploadFile, floor_label: str) -> PlanFile:
    base = await store_upload(project_id, "plans", file)
    return PlanFile(floor_label=floor_label, **base.model_dump())


async def store_photo(project_id: str, file: UploadFile, kind: str, room_id: str | None) -> PhotoFile:
    base = await store_upload(project_id, "photos", file)
    return PhotoFile(kind=kind, room_id=room_id, **base.model_dump())


async def store_invoice(project_id: str, file: UploadFile) -> MaterialInvoiceFile:
    base = await store_upload(project_id, "invoices", file)
    return MaterialInvoiceFile(**base.model_dump())
