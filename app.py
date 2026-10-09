
from flask import Flask, jsonify, request

from google.auth.exceptions import GoogleAuthError
from googleapiclient.errors import HttpError

from validators import (
    validar_entrega,
    validar_actualizacion_horario,
    ErrorValidacion
)

from calendar_service import (
    crear_evento_entrega,
    actualizar_horario_entrega
)


app = Flask(__name__)


# -----------------------------------------
# HEALTH CHECK
# -----------------------------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "servicio": "pruebas-integracion-emila"
    }), 200


# -----------------------------------------
# POST - CREAR ENTREGA
# -----------------------------------------

@app.route("/api/entregas", methods=["POST"])
def crear_entrega():

    if not request.is_json:
        return jsonify({
            "ok": False,
            "error": "Debes enviar Content-Type: application/json."
        }), 415

    datos = request.get_json(silent=True)

    if datos is None:
        return jsonify({
            "ok": False,
            "error": "El JSON enviado no es valido."
        }), 400

    try:
        entrega = validar_entrega(datos)

    except ErrorValidacion as error:
        return jsonify({
            "ok": False,
            "mensaje": "Error de validacion.",
            "errores": error.errores
        }), 400

    try:
        evento = crear_evento_entrega(entrega)

    except FileNotFoundError:
        app.logger.exception("Token OAuth no encontrado.")

        return jsonify({
            "ok": False,
            "error": "No se encontro el token OAuth de Google."
        }), 503

    except (GoogleAuthError, RuntimeError, ValueError):
        app.logger.exception("Error de autenticacion.")

        return jsonify({
            "ok": False,
            "error": "No se pudo autenticar con Google Calendar."
        }), 503

    except HttpError as error:
        app.logger.exception("Error de Google Calendar.")

        return jsonify({
            "ok": False,
            "error": "Error al crear el evento en Google Calendar.",
            "codigo_google": error.resp.status
        }), 502

    except Exception:
        app.logger.exception("Error interno.")

        return jsonify({
            "ok": False,
            "error": "Ocurrio un error interno."
        }), 500

    return jsonify({
        "ok": True,
        "mensaje": "Entrega registrada en Google Calendar.",
        "evento": {
            "id": evento.get("id"),
            "titulo": evento.get("summary"),
            "enlace": evento.get("htmlLink"),
            "inicio": evento.get("start", {}).get("dateTime"),
            "fin": evento.get("end", {}).get("dateTime")
        }
    }), 201


# -----------------------------------------
# PATCH - MODIFICAR HORARIO DE ENTREGA
# -----------------------------------------

@app.route(
    "/api/entregas/<string:evento_id>",
    methods=["PATCH"]
)
def modificar_entrega(evento_id):

    if not request.is_json:
        return jsonify({
            "ok": False,
            "error": "Debes enviar Content-Type: application/json."
        }), 415

    datos = request.get_json(silent=True)

    if datos is None:
        return jsonify({
            "ok": False,
            "error": "El JSON enviado no es valido."
        }), 400

    # Validar nuevo horario
    try:
        horario = validar_actualizacion_horario(datos)

    except ErrorValidacion as error:
        return jsonify({
            "ok": False,
            "mensaje": "Error de validacion.",
            "errores": error.errores
        }), 400

    # Modificar evento en Google Calendar
    try:
        evento = actualizar_horario_entrega(
            evento_id,
            horario
        )

    except FileNotFoundError:
        app.logger.exception("Token OAuth no encontrado.")

        return jsonify({
            "ok": False,
            "error": "No se encontro el token OAuth de Google."
        }), 503

    except (GoogleAuthError, RuntimeError, ValueError):
        app.logger.exception("Error de autenticacion.")

        return jsonify({
            "ok": False,
            "error": "No se pudo autenticar con Google Calendar."
        }), 503

    except HttpError as error:
        codigo = error.resp.status

        app.logger.exception(
            "Google Calendar rechazo la actualizacion."
        )

        if codigo in (404, 410):
            return jsonify({
                "ok": False,
                "error": "El evento no existe o ya no esta disponible."
            }), 404

        return jsonify({
            "ok": False,
            "error": "Error al actualizar el evento.",
            "codigo_google": codigo
        }), 502

    except Exception:
        app.logger.exception("Error inesperado.")

        return jsonify({
            "ok": False,
            "error": "Ocurrio un error interno."
        }), 500

    return jsonify({
        "ok": True,
        "mensaje": "Entrega actualizada en Google Calendar.",
        "evento": {
            "id": evento.get("id"),
            "titulo": evento.get("summary"),
            "enlace": evento.get("htmlLink"),
            "inicio": evento.get("start", {}).get("dateTime"),
            "fin": evento.get("end", {}).get("dateTime")
        }
    }), 200


# -----------------------------------------
# INICIAR SERVIDOR
# -----------------------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
