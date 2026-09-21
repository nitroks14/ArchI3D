from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.schemas import User
from app.material_invoices.schemas import ExtractedMaterialResult
from app.material_invoices.service import extract_material_characteristics, extract_text
from app.projects.dependencies import get_owned_project_state
from app.projects.models import ProjectState
from app.projects.store import get_project_store
from app.shared.base import CamelModel
from app.storage.factory import get_storage_backend
from app.wall_profiles.service import upsert_profile_from_wall

router = APIRouter(prefix="/projects", tags=["material-invoices"])


class LinkInvoiceRequest(CamelModel):
    room_id: str
    wall_id: str


def _get_invoice(state: ProjectState, invoice_id: str):
    invoice = next((i for i in state.invoices if i.id == invoice_id), None)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Facture introuvable")
    return invoice


@router.post("/{project_id}/invoices/{invoice_id}/extract", response_model=ExtractedMaterialResult)
def extract_invoice(
    invoice_id: str,
    state: ProjectState = Depends(get_owned_project_state),
    current_user: User = Depends(get_current_user),
) -> ExtractedMaterialResult:
    invoice = _get_invoice(state, invoice_id)

    file_bytes = get_storage_backend().read(invoice.storage_key)
    ocr_text = extract_text(file_bytes, invoice.content_type)
    invoice.ocr_text = ocr_text

    try:
        extracted = extract_material_characteristics(ocr_text, current_user)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    invoice.extracted = extracted.model_dump(by_alias=True)
    get_project_store().save(state)
    return extracted


@router.post("/{project_id}/invoices/{invoice_id}/link")
def link_invoice(
    invoice_id: str, payload: LinkInvoiceRequest, state: ProjectState = Depends(get_owned_project_state)
) -> dict:
    invoice = _get_invoice(state, invoice_id)
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

    # Capitalise la composition de paroi issue de la facture comme profil reutilisable.
    upsert_profile_from_wall(state.wall_assembly_profiles, wall)

    get_project_store().save(state)
    return {"wallId": wall.id, "layers": [layer.model_dump(by_alias=True) for layer in wall.layers]}
