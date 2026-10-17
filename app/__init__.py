import os

from flask import Flask

from app.db import chiudi_connessione


def create_app(configurazione: dict | None = None) -> Flask:
    """
    Crea e configura l'applicazione: prima i valori dell'ambiente (.env), poi quelli passati
    come parametro, che usano i test.
    Returns: l'applicazione Flask.
    """
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        DB_HOST=os.environ.get("DB_HOST", "localhost"),
        DB_PORT=int(os.environ.get("DB_PORT", "3306")),
        DB_USER=os.environ.get("DB_USER"),
        DB_PASSWORD=os.environ.get("DB_PASSWORD"),
        DB_NAME=os.environ.get("DB_NAME"),
    )
    if configurazione is not None:
        app.config.update(configurazione)
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY mancante: copia .env.example in .env e genera la chiave.")

    app.teardown_appcontext(chiudi_connessione)
    return app
