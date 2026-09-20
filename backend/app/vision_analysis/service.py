"""
Analyse vision IA d'une photo interieure/exterieure : materiaux apparents, type d'ouvertures,
etat apparent de l'isolation, equipements visibles, suggestion de type/nom de piece.
Utilise le provider IA actif (Gemini par defaut, Claude en option - cf app/ai_provider).
"""
from app.ai_provider.factory import get_ai_provider
from app.auth.schemas import User
from app.shared.geo import cardinal_from_azimuth
from app.vision_analysis.schemas import AerialImageAnalysisResult, PhotoAnalysisResult

ANALYSIS_INSTRUCTION = """
Tu es un expert batiment/thermique qui analyse une photo interieure ou exterieure d'une maison.
Reponds avec un objet JSON de la forme exacte :
{
  "materials": ["liste des materiaux apparents, ex: enduit, bardage bois, brique, beton"],
  "opening_types": ["types d'ouvertures visibles, ex: fenetre double vitrage PVC, porte bois"],
  "apparent_insulation_state": "bonne|moyenne|mauvaise|indeterminee",
  "equipment": ["equipements visibles, ex: radiateur, chaudiere, VMC, poele a bois"],
  "suggested_room_type": "kitchen|bedroom|living_room|bathroom|hallway|garage|other|null",
  "suggested_room_name": "nom de piece propose en francais, ou null si photo exterieure",
  "suggested_cardinal_orientation": "N|NE|E|SE|S|SW|W|NW|null",
  "heavy_thermal_mass_elements_detected": ["elements massifs visibles pouvant indiquer une forte inertie thermique, ex: cheminee en pierre, poele de masse, chape beton apparente, mobilier massif en bois important - liste vide si aucun"],
  "confidence": "faible|moyenne|elevee"
}
Si une information n'est pas visible, laisse une liste vide ou "indeterminee"/null. Ne fais pas
d'hypothese non fondee sur l'image.
"""

COMPASS_HINT_TEMPLATE = (
    "\n\nIndice supplementaire (a corroborer avec l'image, ne pas suivre aveuglement) : cette "
    "photo exterieure a ete prise avec un cap boussole releve de {heading:.0f} degres "
    "(orientation approximative : {cardinal}). Si la photo montre une facade, utilise cet indice "
    "pour affiner suggested_cardinal_orientation."
)


def analyze_photo(
    image_bytes: bytes,
    mime_type: str,
    user: User | None = None,
    compass_heading_deg: float | None = None,
) -> PhotoAnalysisResult:
    instruction = ANALYSIS_INSTRUCTION
    if compass_heading_deg is not None:
        instruction += COMPASS_HINT_TEMPLATE.format(
            heading=compass_heading_deg, cardinal=cardinal_from_azimuth(compass_heading_deg)
        )
    raw = get_ai_provider(user).analyze_image(image_bytes, mime_type, instruction)
    return PhotoAnalysisResult.model_validate(raw)


AERIAL_ANALYSIS_INSTRUCTION = """
Tu es un expert batiment/thermique qui analyse une image aerienne (vue du dessus) d'une maison,
en particulier sa toiture. Reponds avec un objet JSON de la forme exacte :
{
  "roof_shape": "description sommaire de la forme de toiture visible, ou null",
  "solar_panels_detected": true ou false,
  "solar_panels_area_estimate_m2": nombre (surface approximative des panneaux visibles en m2) ou null,
  "solar_panels_location_hint": "description sommaire de la position sur la toiture (ex: pan sud, pan principal) ou null",
  "confidence": "faible|moyenne|elevee"
}
Ne fais pas d'hypothese non fondee sur l'image ; si aucun panneau n'est visible,
solar_panels_detected doit etre false et les champs associes null.
"""


def analyze_aerial_image(
    image_bytes: bytes, mime_type: str, user: User | None = None
) -> AerialImageAnalysisResult:
    """
    Analyse dediee a l'image aerienne : forme de toiture + detection/position approximative des
    panneaux solaires existants (cf SolarInstallation, backend/app/shared/schemas.py). Point
    d'integration vision IA pour la detection automatique - la position precise par pan de toit
    et l'orientation/inclinaison restent a affiner en V2 (segmentation par facade/pan).
    """
    raw = get_ai_provider(user).analyze_image(image_bytes, mime_type, AERIAL_ANALYSIS_INSTRUCTION)
    return AerialImageAnalysisResult.model_validate(raw)
