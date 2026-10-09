
import os

from dotenv import load_dotenv
from flask import Flask, jsonify

load_dotenv()

from auth import auth_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]

app.register_blueprint(auth_bp)


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "pruebas-integracion-emila",
        "message": "API Flask funcionando correctamente"
    }), 200
