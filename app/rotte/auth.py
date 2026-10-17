from flask import Blueprint, redirect, render_template, request, session, url_for

from app.db import ottieni_connessione
from app.limiti import LIMITE_TENTATIVI_LOGIN, limiter, tentativo_fallito
from app.servizi.auth import AuthService

bp = Blueprint("auth", __name__, url_prefix="/auth")

MESSAGGIO_LOGIN_ERRATO = "Email o password non corretti."


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit(LIMITE_TENTATIVI_LOGIN, methods=["POST"], deduct_when=tentativo_fallito)
def login():
    """
    Login del proprietario. Dopo il controllo della password la sessione viene svuotata e riceve
    solo l'id dell'utente (protezione dalla session fixation). Ogni errore ha lo stesso messaggio.
    """
    if request.method == "GET":
        return render_template("auth/login.html")

    email = request.form.get("email", "")
    utente = AuthService(ottieni_connessione()).login(email, request.form.get("password", ""))
    if utente is None:
        return render_template("auth/login.html", errore=MESSAGGIO_LOGIN_ERRATO, email=email), 400

    session.clear()
    session["utente_id"] = utente.id
    session.permanent = True
    return redirect(url_for("proprietario.indice"))


@bp.post("/logout")
def logout():
    """
    Esce dall'area riservata: solo POST (con token CSRF), così un link esterno non può far uscire.
    """
    session.clear()
    return redirect(url_for("pubblico.home"))
