import json
from typing import Any

JSON_SYSTEM_HINT = (
    "Tu dois repondre UNIQUEMENT avec un objet JSON valide, sans texte avant/apres, sans markdown."
)


def parse_json_response(raw_text: str) -> dict[str, Any]:
    """Parse la reponse d'un LLM en JSON, avec repli si le modele a ajoute du texte autour."""
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        start, end = raw_text.find("{"), raw_text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(raw_text[start : end + 1])
        raise
