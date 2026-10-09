
from pathlib import Path

from flask import Blueprint, jsonify, redirect, request, session, url_for
from google_auth_oauthlib.flow import Flow


auth_bp = Blueprint("oauth", __name__)

BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events"
]

REDIRECT_URI = "http://localhost:5001/oauth/callback"


def crear_flujo_oauth(state=None, code_verifier=None):
    flow = Flow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        scopes=SCOPES,
        state=state,
        code_verifier=code_verifier
    )

    flow.redirect_uri = REDIRECT_URI
    return flow


@auth_bp.get("/oauth/login")
def iniciar_autorizacion():
    flow = crear_flujo_oauth()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    # Guardar los valores necesarios para completar OAuth
    session["oauth_state"] = state
    session["oauth_code_verifier"] = flow.code_verifier

    return redirect(authorization_url)


@auth_bp.get("/oauth/callback")
def recibir_autorizacion():
    if request.args.get("error"):
        return jsonify({
            "error": "Autorizacion denegada por Google"
        }), 400

    state = session.pop("oauth_state", None)
    code_verifier = session.pop("oauth_code_verifier", None)

    # Validar la sesion y el estado de OAuth
    if not state or not code_verifier:
        return jsonify({
            "error": "Sesion OAuth invalida o incompleta"
        }), 400

    if request.args.get("state") != state:
        return jsonify({
            "error": "El estado OAuth no coincide"
        }), 400

    # Recuperar el verificador PKCE original
    flow = crear_flujo_oauth(
        state=state,
        code_verifier=code_verifier
    )

    # Intercambiar el codigo de Google por los tokens
    flow.fetch_token(
        authorization_response=request.url
    )

    # Guardar las credenciales localmente
    TOKEN_FILE.write_text(
        flow.credentials.to_json(),
        encoding="utf-8"
    )

    return redirect(url_for("oauth.autorizacion_exitosa"))


@auth_bp.get("/oauth/success")
def autorizacion_exitosa():
    if not TOKEN_FILE.exists():
        return jsonify({
            "error": "No hay credenciales guardadas"
        }), 401

    return jsonify({
        "status": "ok",
        "message": "Google Calendar autorizado correctamente"
    }), 200
