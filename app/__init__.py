import os
from datetime import datetime, timedelta

from flask import Flask, render_template
from flask_wtf.csrf import CSRFError, CSRFProtect

from app.comandi import crea_proprietario
from app.db import chiudi_connessione
from app.eccezioni import NonTrovatoError
from app.formato import descrivi_stato_apertura, euro, ora, telefono_leggibile
from app.limiti import limiter
from app.rotte import auth, proprietario, pubblico
from app.sicurezza import crea_aggiungi_header

csrf = CSRFProtect()

MESSAGGI_ERRORE = {
    404: "Pagina non trovata.",
    405: "Operazione non consentita.",
    429: "Troppi tentativi: aspetta un minuto e riprova.",
    500: "Si è verificato un errore: riprova più tardi.",
}


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
    produzione = os.environ.get("PRODUZIONE") == "1"
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        DB_HOST=os.environ.get("DB_HOST", "localhost"),
        DB_PORT=int(os.environ.get("DB_PORT", "3306")),
        DB_USER=os.environ.get("DB_USER"),
        DB_PASSWORD=os.environ.get("DB_PASSWORD"),
        DB_NAME=os.environ.get("DB_NAME"),
        PRODUZIONE=produzione,
        # Cookie di sessione: non leggibile da JavaScript, non inviato da altri siti nei POST,
        # solo HTTPS in produzione; la sessione dura al massimo 8 ore.
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=produzione,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    )
    if configurazione is not None:
        app.config.update(configurazione)
        if "PRODUZIONE" in configurazione:
            app.config["SESSION_COOKIE_SECURE"] = configurazione["PRODUZIONE"]
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY mancante: copia .env.example in .env e genera la chiave.")

    app.teardown_appcontext(chiudi_connessione)
    app.after_request(crea_aggiungi_header(app.config["PRODUZIONE"]))
    csrf.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(pubblico.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(proprietario.bp)
    app.cli.add_command(crea_proprietario)

    app.add_template_filter(euro)
    app.add_template_filter(ora)
    app.add_template_filter(telefono_leggibile)
    app.add_template_global(descrivi_stato_apertura)
    app.context_processor(lambda: {"anno": datetime.now().year})

    for codice, messaggio in MESSAGGI_ERRORE.items():
        app.register_error_handler(codice, lambda errore, c=codice, m=messaggio: pagina_errore(c, m))
    app.register_error_handler(NonTrovatoError, lambda errore: pagina_errore(404, str(errore)))
    app.register_error_handler(
        CSRFError,
        lambda errore: pagina_errore(400, "Modulo scaduto o non valido: ricarica la pagina e riprova."),
    )
    return app
