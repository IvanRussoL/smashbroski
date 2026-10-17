import os

from flask import Flask


def create_app(configurazione: dict | None = None) -> Flask:
    """
    Crea e configura l'applicazione: prima i valori dell'ambiente (.env), poi quelli passati
    come parametro, che usano i test.
    Returns: l'applicazione Flask.
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    if configurazione is not None:
        app.config.update(configurazione)
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY mancante: copia .env.example in .env e genera la chiave.")
    return app
