from typing import Any

from app.ai_provider.base import AIProvider
from app.ai_provider.json_utils import JSON_SYSTEM_HINT, parse_json_response


class GeminiProvider(AIProvider):
    """
    Implementation par defaut (gratuite) via l'API Gemini (Google AI Studio).
    Cle API a creer gratuitement sur https://ai.google.dev puis a renseigner dans GEMINI_API_KEY.
    """

    def __init__(self, api_key: str, model_name: str):
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY manquante. Cree une cle gratuite sur https://ai.google.dev "
                "et renseigne-la dans le fichier .env du backend."
            )
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name)

    def analyze_image(self, image_bytes: bytes, mime_type: str, instruction: str) -> dict[str, Any]:
        response = self._model.generate_content(
            [f"{JSON_SYSTEM_HINT}\n\n{instruction}", {"mime_type": mime_type, "data": image_bytes}],
            generation_config={"response_mime_type": "application/json"},
        )
        return parse_json_response(response.text)

    def generate_structured(self, prompt: str) -> dict[str, Any]:
        response = self._model.generate_content(
            f"{JSON_SYSTEM_HINT}\n\n{prompt}",
            generation_config={"response_mime_type": "application/json"},
        )
        return parse_json_response(response.text)

