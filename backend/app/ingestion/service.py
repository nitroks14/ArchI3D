"""Sauvegarde des fichiers uploades (image aerienne, plans, photos, factures) via le storage backend."""
from uuid import uuid4

from fastapi import UploadFile

from app.projects.models import MaterialInvoiceFile, PhotoFile, PlanFile, UploadedFile
from app.storage.base import build_project_key
from app.storage.factory import get_storage_backend


async def store_upload(owner_id: str, project_id: str, category: str, file: UploadFile) -> UploadedFile:
    data = await file.read()
    safe_name = (file.filename or "upload.bin").replace("/", "_")
    key = build_project_key(owner_id, project_id, category, f"{uuid4().hex[:8]}_{safe_name}")
    url = get_storage_backend().save(key, data, file.content_type or "application/octet-stream")
    return UploadedFile(
        id=f"{category}_{uuid4().hex[:8]}",
        storage_key=key,
        url=url,
        filename=file.filename or "upload.bin",
        content_type=file.content_type or "application/octet-stream",
    )


async def store_plan(owner_id: str, project_id: str, file: UploadFile, floor_label: str) -> PlanFile:
    base = await store_upload(owner_id, project_id, "plans", file)
    return PlanFile(floor_label=floor_label, **base.model_dump())


async def store_photo(
    owner_id: str,
    project_id: str,
    file: UploadFile,
    kind: str,
    room_id: str | None,
    compass_heading_deg: float | None = None,
) -> PhotoFile:
    base = await store_upload(owner_id, project_id, "photos", file)
    return PhotoFile(
        kind=kind, room_id=room_id, compass_heading_deg=compass_heading_deg, **base.model_dump()
    )


async def store_invoice(owner_id: str, project_id: str, file: UploadFile) -> MaterialInvoiceFile:
    base = await store_upload(owner_id, project_id, "invoices", file)
    return MaterialInvoiceFile(**base.model_dump())
