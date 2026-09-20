"""
Extraction de texte (OCR) a partir d'images (labels de pieces sur un plan, factures materiaux
scannees) et de PDF texte (factures materiaux exportees en PDF).

Degradation gracieuse : si le binaire systeme "tesseract" n'est pas installe (cf Dockerfile),
l'OCR image renvoie une chaine vide plutot que de faire planter la requete - les pipelines
appelants (nommage de pieces, extraction facture) doivent prevoir ce cas et retomber sur une
alternative (heuristique simple ou saisie utilisateur).
"""
import io
import logging

logger = logging.getLogger(__name__)


def extract_text_from_image(image_bytes: bytes, lang: str = "fra") -> str:
    try:
        import pytesseract
        from PIL import Image

        image = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(image, lang=lang).strip()
    except Exception as exc:  # tesseract non installe, image corrompue, etc.
        logger.warning("OCR image indisponible (%s) - poursuite sans texte extrait.", exc)
        return ""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extrait le texte d'un PDF textuel. Les PDF scannes (image pure) ne sont pas geres en V1."""
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as exc:
        logger.warning("Extraction texte PDF indisponible (%s).", exc)
        return ""
