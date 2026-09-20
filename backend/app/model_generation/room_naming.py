"""Heuristique simple de reconnaissance du nom/type de piece a partir du texte OCR d'un plan."""

_KEYWORDS: dict[str, tuple[str, str]] = {
    # mot-cle (minuscule, sans accent) -> (room_type, nom francais affiche)
    "cuisine": ("kitchen", "Cuisine"),
    "chambre": ("bedroom", "Chambre"),
    "salon": ("living_room", "Salon"),
    "sejour": ("living_room", "Sejour"),
    "salle a manger": ("living_room", "Salle a manger"),
    "salle de bain": ("bathroom", "Salle de bain"),
    "sdb": ("bathroom", "Salle de bain"),
    "salle d'eau": ("bathroom", "Salle d'eau"),
    "wc": ("other", "WC"),
    "toilettes": ("other", "Toilettes"),
    "garage": ("garage", "Garage"),
    "bureau": ("other", "Bureau"),
    "entree": ("hallway", "Entree"),
    "couloir": ("hallway", "Couloir"),
    "cellier": ("other", "Cellier"),
    "buanderie": ("other", "Buanderie"),
    "dressing": ("other", "Dressing"),
    "garde-robe": ("other", "Dressing"),
}


def _normalize(text: str) -> str:
    replacements = str.maketrans("eaiou", "eaiou")  # placeholder, on normalise juste la casse
    return text.lower().translate(replacements)


def guess_room_from_ocr_text(ocr_text: str) -> tuple[str | None, str | None]:
    """Retourne (room_type, nom_suggere) a partir du texte OCR lu dans la zone de la piece."""
    if not ocr_text:
        return None, None
    normalized = _normalize(ocr_text)
    for keyword, (room_type, label) in _KEYWORDS.items():
        if keyword in normalized:
            return room_type, label
    # Aucun mot-cle reconnu : on garde le texte brut OCR comme suggestion (nettoye)
    cleaned = ocr_text.strip().splitlines()[0][:40] if ocr_text.strip() else None
    return None, cleaned or None
