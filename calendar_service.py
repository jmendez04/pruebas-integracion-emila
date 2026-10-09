
import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events"
]


def obtener_servicio_calendar():
    nombre_token = os.getenv(
        "GOOGLE_TOKEN_FILE",
        "token.json"
    )

    ruta_token = Path(nombre_token)

    if not ruta_token.is_absolute():
        ruta_token = BASE_DIR / ruta_token

    if not ruta_token.is_file():
        raise FileNotFoundError(
            "No se encontro el token de Google. "
            "Ejecuta primero la autenticacion OAuth."
        )

    credenciales = Credentials.from_authorized_user_file(
        str(ruta_token),
        SCOPES
    )

    if not credenciales.valid:
        if credenciales.expired and credenciales.refresh_token:
            credenciales.refresh(Request())

            ruta_token.write_text(
                credenciales.to_json(),
                encoding="utf-8"
            )
        else:
            raise RuntimeError(
                "Las credenciales OAuth no son validas."
            )

    return build(
        "calendar",
        "v3",
        credentials=credenciales,
        cache_discovery=False
    )


# -----------------------------------------
# POST - CREAR EVENTO
# -----------------------------------------

def crear_evento_entrega(datos):
    servicio = obtener_servicio_calendar()

    descripcion = (
        f"Pedido: {datos['pedido_id']}\n"
        f"Cliente: {datos['cliente']}\n"
        f"Direccion: {datos['direccion']}"
    )

    if datos["observaciones"]:
        descripcion += (
            f"\nObservaciones: {datos['observaciones']}"
        )

    evento = {
        "summary": (
            f"Entrega EMILA - Pedido {datos['pedido_id']}"
        ),
        "location": datos["direccion"],
        "description": descripcion,
        "start": {
            "dateTime": datos["inicio"]
        },
        "end": {
            "dateTime": datos["fin"]
        }
    }

    calendario_id = os.getenv(
        "GOOGLE_CALENDAR_ID",
        "primary"
    )

    evento_creado = (
        servicio.events()
        .insert(
            calendarId=calendario_id,
            body=evento
        )
        .execute()
    )

    return evento_creado


# -----------------------------------------
# PATCH - ACTUALIZAR HORARIO
# -----------------------------------------

def actualizar_horario_entrega(evento_id, datos):
    servicio = obtener_servicio_calendar()

    calendario_id = os.getenv(
        "GOOGLE_CALENDAR_ID",
        "primary"
    )

    cambios = {
        "start": {
            "dateTime": datos["inicio"]
        },
        "end": {
            "dateTime": datos["fin"]
        }
    }

    evento_actualizado = (
        servicio.events()
        .patch(
            calendarId=calendario_id,
            eventId=evento_id,
            body=cambios
        )
        .execute()
    )

    return evento_actualizado


# -----------------------------------------
# DELETE - ELIMINAR EVENTO
# -----------------------------------------

def eliminar_evento_entrega(evento_id):
    servicio = obtener_servicio_calendar()

    calendario_id = os.getenv(
        "GOOGLE_CALENDAR_ID",
        "primary"
    )

    # Consultar el evento antes de eliminarlo
    evento = (
        servicio.events()
        .get(
            calendarId=calendario_id,
            eventId=evento_id
        )
        .execute()
    )

    # Evitar eliminar eventos ajenos a las pruebas EMILA
    if not evento.get("summary", "").startswith(
        "Entrega EMILA - Pedido "
    ):
        raise PermissionError(
            "Solo se pueden eliminar eventos de entrega EMILA."
        )

    # Eliminar evento de Google Calendar
    (
        servicio.events()
        .delete(
            calendarId=calendario_id,
            eventId=evento_id
        )
        .execute()
    )

    return {
        "id": evento.get("id"),
        "titulo": evento.get("summary")
    }
