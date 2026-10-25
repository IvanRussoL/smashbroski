from flask import Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for

from app.db import ottieni_connessione
from app.eccezioni import DatiNonValidiError
from app.limiti import limita_tentativi
from app.repository.utente import UtenteRepository
from app.servizi.auth import AuthService
from app.servizi.due_passaggi import MESSAGGIO_CODICE_ERRATO, DuePassaggiService
from app.servizi.tentativi import AMBITO_CODICE, AMBITO_LOGIN, messaggio_tentativi_rimasti
from app.sessione import apri_sessione, attendi_codice, utente_in_attesa

bp = Blueprint("auth", __name__, url_prefix="/auth")

MESSAGGIO_LOGIN_ERRATO = "Email o password non corretti."


@bp.after_request
def non_indicizzare(risposta):
    """
    Le pagine di accesso non finiscono nei risultati dei motori di ricerca. Un header invece di
    una riga in robots.txt, che renderebbe pubblico l'elenco degli indirizzi riservati.
    """
    risposta.headers["X-Robots-Tag"] = "noindex, nofollow"
    return risposta


@bp.route("/login", methods=["GET", "POST"])
@limita_tentativi(AMBITO_LOGIN)
def login():
    """
    Login del proprietario. Dopo il controllo della password la sessione viene svuotata e riceve
    solo l'id dell'utente e l'impronta della password (app/sessione.py). Ogni errore ha lo stesso
    messaggio, seguito dai tentativi rimasti (uguali per email e password sbagliate).
    Con la verifica in due passaggi attiva la password giusta porta alla pagina del codice.
    """
    if request.method == "GET":
        return render_template("auth/login.html")

    email = request.form.get("email", "")
    utente = AuthService(ottieni_connessione()).login(email, request.form.get("password", ""))
    if utente is None:
        g.password_sbagliata = True
        errore = MESSAGGIO_LOGIN_ERRATO
        if "tentativi_rimasti" in g:
            errore += " " + messaggio_tentativi_rimasti(g.tentativi_rimasti)
        return render_template("auth/login.html", errore=errore, email=email), 400

    if utente.totp_attivo:
        attendi_codice(utente)
        return redirect(url_for("auth.codice"))
    apri_sessione(utente)
    return redirect(url_for("proprietario.indice"))


@bp.route("/codice", methods=["GET", "POST"])
@limita_tentativi(AMBITO_CODICE)
def codice():
    """
    Secondo passaggio dell'accesso: codice di 6 cifre dall'app del telefono o codice di riserva.
    Si arriva solo dopo la password giusta, entro 5 minuti; stesso limite di 5 errori al minuto.
    """
    utente_id = utente_in_attesa()
    utente = UtenteRepository(ottieni_connessione()).leggi_per_id(utente_id) if utente_id else None
    if utente is None or not utente.attivo or not utente.totp_attivo:
        session.clear()
        flash("Per sicurezza il codice va scritto entro 5 minuti dalla password: entra di nuovo.")
        return redirect(url_for("auth.login"))
    if request.method == "GET":
        return render_template("auth/codice.html")

    try:
        corretto = DuePassaggiService(ottieni_connessione(), current_app.secret_key).verifica(
            utente, request.form.get("codice", "")
        )
    except DatiNonValidiError as errore:
        return render_template("auth/codice.html", errore=" ".join(errore.messaggi)), 400
    if not corretto:
        g.password_sbagliata = True
        errore = MESSAGGIO_CODICE_ERRATO
        if "tentativi_rimasti" in g:
            errore += " " + messaggio_tentativi_rimasti(g.tentativi_rimasti)
        return render_template("auth/codice.html", errore=errore), 400

    apri_sessione(utente)
    rimasti = DuePassaggiService(ottieni_connessione(), current_app.secret_key).codici_riserva_rimasti(utente.id)
    if rimasti <= 3:
        flash(f"Ti restano {rimasti} codici di riserva: creane di nuovi da \"Verifica in due passaggi\".")
    return redirect(url_for("proprietario.indice"))


@bp.post("/logout")
def logout():
    """
    Esce dall'area riservata: solo POST (con token CSRF), così un link esterno non può far uscire.
    """
    session.clear()
    return redirect(url_for("pubblico.home"))
