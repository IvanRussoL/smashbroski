from flask import Blueprint, redirect, render_template, request, session, url_for

from app.db import ottieni_connessione
from app.limiti import limita_tentativi
from app.servizi.auth import AuthService
from app.servizi.tentativi import AMBITO_LOGIN
from app.sessione import apri_sessione

bp = Blueprint("auth", __name__, url_prefix="/auth")

MESSAGGIO_LOGIN_ERRATO = "Email o password non corretti."


@bp.route("/login", methods=["GET", "POST"])
@limita_tentativi(AMBITO_LOGIN)
def login():
    """
    Login del proprietario. Dopo il controllo della password la sessione viene svuotata e riceve
    solo l'id dell'utente e l'impronta della password (app/sessione.py). Ogni errore ha lo stesso messaggio.
    """
    if request.method == "GET":
        return render_template("auth/login.html")

    email = request.form.get("email", "")
    utente = AuthService(ottieni_connessione()).login(email, request.form.get("password", ""))
    if utente is None:
        return render_template("auth/login.html", errore=MESSAGGIO_LOGIN_ERRATO, email=email), 400

    apri_sessione(utente)
    return redirect(url_for("proprietario.indice"))


@bp.post("/logout")
def logout():
    """
    Esce dall'area riservata: solo POST (con token CSRF), così un link esterno non può far uscire.
    """
    session.clear()
    return redirect(url_for("pubblico.home"))
