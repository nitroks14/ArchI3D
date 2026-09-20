"""
Flow OAuth 2.0 "Authorization Code" avec Google (cf README > Authentification pour la procedure
de creation des identifiants sur Google Cloud Console).

Securite :
- l'ID token retourne par Google est verifie SERVEUR (signature, emetteur, expiration ET
  audience = notre propre GOOGLE_CLIENT_ID) via la bibliotheque officielle google-auth, pas de
  confiance aveugle dans le contenu du token.
- ni le code d'autorisation, ni les tokens Google, ni GOOGLE_CLIENT_SECRET/SESSION_SECRET ne sont
  jamais logges (cf consigne securite).
"""
from urllib.parse import urlencode

import httpx
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.core.config import get_settings

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = "openid email profile"


class GoogleOAuthError(RuntimeError):
    pass


def build_authorize_url(state: str) -> str:
    settings = get_settings()
    if not settings.google_client_id:
        raise GoogleOAuthError(
            "GOOGLE_CLIENT_ID manquant. Cf README > Authentification pour creer des identifiants "
            "OAuth gratuits sur https://console.cloud.google.com et les renseigner dans le .env."
        )
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code_for_tokens(code: str) -> dict:
    settings = get_settings()
    response = httpx.post(
        TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=10.0,
    )
    if response.status_code != 200:
        # ne pas inclure le corps de la reponse dans l'exception : peut contenir des details
        # sensibles selon la nature de l'erreur cote Google.
        raise GoogleOAuthError(f"Echange du code d'autorisation Google echoue (HTTP {response.status_code})")
    return response.json()


def verify_id_token(id_token_str: str) -> dict:
    """Verifie signature + emetteur + expiration + audience (=notre GOOGLE_CLIENT_ID). Leve
    google.auth.exceptions.GoogleAuthError si le token est invalide - a capter par l'appelant."""
    settings = get_settings()
    return google_id_token.verify_oauth2_token(
        id_token_str, google_requests.Request(), audience=settings.google_client_id
    )
