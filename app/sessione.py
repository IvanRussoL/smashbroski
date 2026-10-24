import hmac
from hashlib import sha256

from flask import current_app, session

from app.modelli.utente import Utente


def impronta_password(password_hash: str) -> str:
    """
    Impronta dell'hash della password, salvata nella sessione: se la password cambia, l'impronta
    non corrisponde più e le sessioni aperte su altri dispositivi si chiudono alla richiesta
    successiva. È un HMAC con la SECRET_KEY, perché il cookie di sessione è firmato ma leggibile:
    l'hash vero non deve finirci.
    """
    return hmac.new(current_app.secret_key.encode(), password_hash.encode(), sha256).hexdigest()


def apri_sessione(utente: Utente) -> None:
    """
    Svuota la sessione e la ricrea con l'id dell'utente e l'impronta della sua password
    (protezione dalla session fixation). Usata dopo il login e dopo il cambio della password.
    """
    session.clear()
    session["utente_id"] = utente.id
    session["impronta"] = impronta_password(utente.password_hash)
    session.permanent = True


def sessione_valida(utente: Utente | None) -> bool:
    """
    Returns: True se l'utente esiste, è attivo e la password non è cambiata dopo l'apertura della sessione.
    """
    if utente is None or not utente.attivo:
        return False
    return hmac.compare_digest(session.get("impronta", ""), impronta_password(utente.password_hash))
