"""
Analyse vision IA d'une photo interieure/exterieure : materiaux apparents, type d'ouvertures,
etat apparent de l'isolation, equipements visibles, suggestion de type/nom de piece.
Utilise le provider IA actif (Gemini par defaut, Claude en option - cf app/ai_provider).
"""
from app.ai_provider.factory import get_ai_provider

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
  "confidence": "faible|moyenne|elevee"
}
Si une information n'est pas visible, laisse une liste vide ou "indeterminee"/null. Ne fais pas
d'hypothese non fondee sur l'image.
"""


def analyze_photo(image_bytes: bytes, mime_type: str) -> dict:
    return get_ai_provider().analyze_image(image_bytes, mime_type, ANALYSIS_INSTRUCTION)
