import base64
from typing import Any

from app.ai_provider.base import AIProvider
from app.ai_provider.json_utils import JSON_SYSTEM_HINT, parse_json_response


class ClaudeProvider(AIProvider):
    """
    Implementation alternative via l'API Anthropic (Claude). Non gratuite - a activer
    en mettant AI_PROVIDER=claude et ANTHROPIC_API_KEY dans le .env du backend.
    """

    def __init__(self, api_key: str, model_name: str):
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY manquante. Renseigne-la dans le fichier .env du backend "
                "pour utiliser AI_PROVIDER=claude."
            )
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model_name

    def analyze_image(self, image_bytes: bytes, mime_type: str, instruction: str) -> dict[str, Any]:
        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        message = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{JSON_SYSTEM_HINT}\n\n{instruction}"},
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": mime_type, "data": b64_image},
                        },
                    ],
                }
            ],
        )
        return parse_json_response(message.content[0].text)

    def generate_structured(self, prompt: str) -> dict[str, Any]:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[{"role": "user", "content": f"{JSON_SYSTEM_HINT}\n\n{prompt}"}],
        )
        return parse_json_response(message.content[0].text)

