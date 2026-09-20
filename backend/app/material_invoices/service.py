"""
Pipeline d'ingestion des factures/fiches techniques de materiaux :
OCR (image ou PDF texte) -> extraction structuree via le provider IA actif.
"""
from app.ai_provider.factory import get_ai_provider
from app.auth.schemas import User
from app.material_invoices.schemas import ExtractedMaterialResult
from app.ocr.service import extract_text_from_image, extract_text_from_pdf

EXTRACTION_PROMPT_TEMPLATE = """
Voici le texte brut (OCR) d'une facture ou fiche technique de materiau de construction/isolation :
---
{ocr_text}
---
Extrais les caracteristiques utiles et reponds avec un objet JSON de la forme exacte :
{{
  "material": "nature du materiau, ex: laine de verre, beton cellulaire, PVC double vitrage",
  "product_reference": "reference produit/modele si mentionnee, sinon null",
  "thickness_cm": nombre en centimetres si mentionne, sinon null,
  "r_value": nombre (resistance thermique R en m2.K/W) si mentionne, sinon null,
  "quantity": "quantite/surface/longueur si mentionnee, sinon null"
}}
Si une information est absente du texte, mets null plutot que d'inventer une valeur.
"""


def extract_text(file_bytes: bytes, content_type: str) -> str:
    if content_type == "application/pdf":
        return extract_text_from_pdf(file_bytes)
    return extract_text_from_image(file_bytes)


def extract_material_characteristics(
    ocr_text: str, user: User | None = None
) -> ExtractedMaterialResult:
    if not ocr_text.strip():
        return ExtractedMaterialResult(warning="Aucun texte lisible extrait du document (OCR vide).")
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(ocr_text=ocr_text[:4000])
    raw = get_ai_provider(user).generate_structured(prompt)
    return ExtractedMaterialResult.model_validate(raw)
