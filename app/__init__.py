import os
from datetime import datetime

from flask import Flask, render_template

from app.db import chiudi_connessione
from app.eccezioni import NonTrovatoError
from app.formato import euro, ora, telefono_leggibile, descrivi_stato_apertura
from app.rotte import pubblico
from app.sicurezza import crea_aggiungi_header


def pagina_errore(codice: int, messaggio: str):
    """
    Returns: la pagina di errore del sito con il codice HTTP indicato.
    """
    return render_template("errore.html", codice=codice, messaggio=messaggio), codice


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
        PRODUZIONE=os.environ.get("PRODUZIONE") == "1",
    )
    if configurazione is not None:
        app.config.update(configurazione)
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY mancante: copia .env.example in .env e genera la chiave.")

    app.teardown_appcontext(chiudi_connessione)
    app.after_request(crea_aggiungi_header(app.config["PRODUZIONE"]))
    app.register_blueprint(pubblico.bp)

    app.add_template_filter(euro)
    app.add_template_filter(ora)
    app.add_template_filter(telefono_leggibile)
    app.add_template_global(descrivi_stato_apertura)
    app.context_processor(lambda: {"anno": datetime.now().year})

    app.register_error_handler(404, lambda errore: pagina_errore(404, "Pagina non trovata."))
    app.register_error_handler(NonTrovatoError, lambda errore: pagina_errore(404, str(errore)))
    app.register_error_handler(405, lambda errore: pagina_errore(405, "Operazione non consentita."))
    app.register_error_handler(500, lambda errore: pagina_errore(500, "Si è verificato un errore: riprova più tardi."))
    return app
