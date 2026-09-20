"""
Fabrique du provider IA actif. Pour Gemini, resout en priorite la cle API personnelle de
l'utilisateur courant (cf app/auth/crypto.py + Page "Parametres" du frontend), avec repli sur la
variable d'environnement globale GEMINI_API_KEY si l'utilisateur n'en a pas configure - pratique
pour le dev local sans avoir a creer un compte/cle pour chaque test.

Pas de cache global (contrairement a la V1 initiale) : la cle a utiliser depend de l'utilisateur
courant, donc chaque appel resout une instance dediee.

Limitation connue (documentee) : le SDK google-generativeai configure la cle API de facon
GLOBALE au niveau du module Python (genai.configure()), pas par instance. Sous forte charge
concurrente multi-utilisateurs, deux requetes simultanees utilisant des cles differentes peuvent
en theorie se marcher dessus (race condition au niveau du SDK, pas de notre code). Acceptable
pour ce scaffold V1 mono-instance a usage personnel/demo ; a corriger en V2 en migrant vers un
SDK/pattern supportant une configuration par-requete (ex: google-genai avec un Client() dedie).
"""
import logging

from app.ai_provider.base import AIProvider
from app.auth.schemas import User
from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _resolve_gemini_api_key(user: User | None) -> str:
    settings = get_settings()
    if user and user.gemini_api_key_encrypted:
        from app.auth.crypto import SecretEncryptionError, decrypt_secret

        try:
            return decrypt_secret(user.gemini_api_key_encrypted)
        except SecretEncryptionError:
            logger.warning(
                "Impossible de dechiffrer la cle Gemini de l'utilisateur %s, repli sur la cle globale.",
                user.id,
            )
    return settings.gemini_api_key


def get_ai_provider(user: User | None = None) -> AIProvider:
    settings = get_settings()

    if settings.ai_provider == "claude":
        from app.ai_provider.claude_provider import ClaudeProvider

        return ClaudeProvider(api_key=settings.anthropic_api_key, model_name=settings.anthropic_model)

    from app.ai_provider.gemini_provider import GeminiProvider

    api_key = _resolve_gemini_api_key(user)
    return GeminiProvider(api_key=api_key, model_name=settings.gemini_model)
