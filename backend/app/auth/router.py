"""
Endpoints d'authentification Google OAuth 2.0 (Authorization Code flow) + preferences utilisateur :
- GET    /auth/google/login     -> redirige vers l'ecran de consentement Google
- GET    /auth/google/callback  -> echange le code, verifie l'ID token, pose la session
- POST   /auth/logout           -> efface la session
- GET    /auth/me               -> utilisateur courant (401 si non authentifie)
- PUT    /auth/me/gemini-key    -> enregistre la cle API Gemini personnelle (chiffree au repos)
- DELETE /auth/me/gemini-key    -> supprime la cle API Gemini personnelle

Voir README > Authentification pour la creation des identifiants OAuth (Google Cloud Console).
"""
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse

from app.auth.crypto import encrypt_secret, mask_secret
from app.auth.dependencies import get_current_user
from app.auth.google_oauth import (
    GoogleOAuthError,
    build_authorize_url,
    exchange_code_for_tokens,
    verify_id_token,
)
from app.auth.schemas import PublicUser, User, to_public_user
from app.auth.security import create_session_token
from app.auth.store import get_user_store
from app.core.config import get_settings
from app.shared.base import CamelModel

router = APIRouter(prefix="/auth", tags=["auth"])

OAUTH_STATE_COOKIE = "oauth_state"


@router.get("/google/login")
def google_login() -> RedirectResponse:
    settings = get_settings()
    state = secrets.token_urlsafe(24)

    try:
        authorize_url = build_authorize_url(state)
    except GoogleOAuthError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    redirect = RedirectResponse(authorize_url, status_code=302)
    # Cookie CSRF court-terme, verifie au retour de Google (cf google_callback). Pose/lecture se
    # font toutes deux sur notre propre domaine (navigation top-level) : pas besoin de
    # SameSite=None ici, contrairement au cookie de session final.
    redirect.set_cookie(
        OAUTH_STATE_COOKIE,
        state,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        max_age=300,
        path="/auth",
    )
    return redirect


@router.get("/google/callback")
def google_callback(code: str, state: str, request: Request) -> RedirectResponse:
    settings = get_settings()

    cookie_state = request.cookies.get(OAUTH_STATE_COOKIE)
    if not cookie_state or cookie_state != state:
        raise HTTPException(status_code=400, detail="Etat OAuth invalide (session expiree ou CSRF)")

    try:
        tokens = exchange_code_for_tokens(code)
    except GoogleOAuthError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    id_token_str = tokens.get("id_token")
    if not id_token_str:
        raise HTTPException(status_code=502, detail="Reponse Google inattendue (id_token manquant)")

    try:
        claims = verify_id_token(id_token_str)
    except Exception as exc:  # google-auth leve plusieurs types d'exceptions selon le cas
        raise HTTPException(status_code=401, detail="Verification du token Google echouee") from exc

    google_sub = claims["sub"]
    email = claims.get("email", "")
    display_name = claims.get("name") or email or google_sub

    store = get_user_store()
    user = store.get_by_google_sub(google_sub)
    if user is None:
        user = User(email=email, google_sub=google_sub, display_name=display_name)
    else:
        user.email = email
        user.display_name = display_name
    store.save(user)

    session_token = create_session_token(user)

    redirect = RedirectResponse(settings.frontend_url, status_code=302)
    redirect.delete_cookie(OAUTH_STATE_COOKIE, path="/auth")
    redirect.set_cookie(
        settings.session_cookie_name,
        session_token,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
        max_age=settings.session_max_age_seconds,
        path="/",
    )
    return redirect


@router.post("/logout", status_code=204)
def logout() -> Response:
    settings = get_settings()
    response = Response(status_code=204)
    response.delete_cookie(settings.session_cookie_name, path="/")
    return response


@router.get("/me", response_model=PublicUser)
def me(current_user: User = Depends(get_current_user)) -> PublicUser:
    return to_public_user(current_user)


class GeminiKeyRequest(CamelModel):
    api_key: str


@router.put("/me/gemini-key", response_model=PublicUser)
def set_gemini_key(
    payload: GeminiKeyRequest, current_user: User = Depends(get_current_user)
) -> PublicUser:
    """
    Enregistre la cle API Gemini personnelle de l'utilisateur (creee gratuitement sur
    https://ai.google.dev), chiffree au repos (cf app/auth/crypto.py). Jamais renvoyee en clair -
    seul un apercu masque (ex: "AIza...xyz") est expose ensuite via /auth/me.
    """
    api_key = payload.api_key.strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="Cle API vide")

    current_user.gemini_api_key_encrypted = encrypt_secret(api_key)
    current_user.gemini_api_key_hint = mask_secret(api_key)
    get_user_store().save(current_user)
    return to_public_user(current_user)


@router.delete("/me/gemini-key", response_model=PublicUser)
def clear_gemini_key(current_user: User = Depends(get_current_user)) -> PublicUser:
    current_user.gemini_api_key_encrypted = None
    current_user.gemini_api_key_hint = None
    get_user_store().save(current_user)
    return to_public_user(current_user)
