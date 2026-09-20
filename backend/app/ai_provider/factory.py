from functools import lru_cache

from app.ai_provider.base import AIProvider
from app.core.config import get_settings


@lru_cache
def get_ai_provider() -> AIProvider:
    settings = get_settings()

    if settings.ai_provider == "claude":
        from app.ai_provider.claude_provider import ClaudeProvider

        return ClaudeProvider(api_key=settings.anthropic_api_key, model_name=settings.anthropic_model)

    from app.ai_provider.gemini_provider import GeminiProvider

    return GeminiProvider(api_key=settings.gemini_api_key, model_name=settings.gemini_model)
