from fastapi import APIRouter, HTTPException

from app.material_invoices.schemas import ExtractedMaterialResult
from app.material_invoices.service import extract_material_characteristics, extract_text
from app.projects.store import get_project_store
from app.shared.base import CamelModel
from app.storage.factory import get_storage_backend

router = APIRouter(prefix="/projects", tags=["material-invoices"])


class LinkInvoiceRequest(CamelModel):
    room_id: str
    wall_id: str


def _get_state_and_invoice(project_id: str, invoice_id: str):
    store = get_project_store()
    try:
        state = store.get(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    invoice = next((i for i in state.invoices if i.id == invoice_id), None)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Facture introuvable")
    return store, state, invoice


@router.post("/{project_id}/invoices/{invoice_id}/extract", response_model=ExtractedMaterialResult)
def extract_invoice(project_id: str, invoice_id: str) -> ExtractedMaterialResult:
    store, state, invoice = _get_state_and_invoice(project_id, invoice_id)

    file_bytes = get_storage_backend().read(invoice.storage_key)
    ocr_text = extract_text(file_bytes, invoice.content_type)
    invoice.ocr_text = ocr_text

    try:
        extracted = extract_material_characteristics(ocr_text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    invoice.extracted = extracted.model_dump(by_alias=True)
    store.save(state)
    return extracted


@router.post("/{project_id}/invoices/{invoice_id}/link")
def link_invoice(project_id: str, invoice_id: str, payload: LinkInvoiceRequest) -> dict:
    store, state, invoice = _get_state_and_invoice(project_id, invoice_id)
    if invoice.extracted is None:
        raise HTTPException(status_code=400, detail="Lance d'abord l'extraction de la facture")
    if state.building_model is None:
        raise HTTPException(status_code=400, detail="Aucun modele de batiment genere")

    room = next(
        (r for f in state.building_model.floors for r in f.rooms if r.id == payload.room_id), None
    )
    if room is None:
        raise HTTPException(status_code=404, detail="Piece introuvable dans le modele")
    wall = next((w for w in room.walls if w.id == payload.wall_id), None)
    if wall is None:
        raise HTTPException(status_code=404, detail="Paroi introuvable dans cette piece")

    from app.shared.schemas import MaterialLayer

    extracted = ExtractedMaterialResult.model_validate(invoice.extracted)
    wall.layers.append(
        MaterialLayer(
            source="invoice",
            material_ref=extracted.material,
            thickness_cm=extracted.thickness_cm,
            r_value=extracted.r_value,
            product_reference=extracted.product_reference,
            invoice_id=invoice.id,
        )
    )
    invoice.linked_room_id = payload.room_id
    invoice.linked_wall_id = payload.wall_id
    store.save(state)
    return {"wallId": wall.id, "layers": [layer.model_dump(by_alias=True) for layer in wall.layers]}
