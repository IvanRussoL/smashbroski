import hmac
import time
from hashlib import sha256

from flask import current_app, session

from app.modelli.utente import Utente

# Timeout controllati dal server (OWASP WSTG, Testing Session Timeout; ASVS 3.3 e 3.4): dopo un'ora
# senza aprire pagine dell'area, o 8 ore dopo il login anche se si usa l'area, bisogna rientrare.
# Senza questi controlli Flask rinnoverebbe il cookie a ogni richiesta e la sessione non finirebbe mai.
INATTIVITA_MASSIMA_SECONDI = 60 * 60
DURATA_MASSIMA_SECONDI = 8 * 60 * 60


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
    adesso = int(time.time())
    session.clear()
    session["utente_id"] = utente.id
    session["impronta"] = impronta_password(utente.password_hash)
    session["entrato_il"] = adesso
    session["ultima_attivita"] = adesso
    session.permanent = True


def sessione_scaduta() -> bool:
    """
    Returns: True se è passata più di un'ora dall'ultima pagina dell'area o più di 8 ore dal login.
    Le ore stanno nel cookie firmato con la SECRET_KEY: chi lo legge non può cambiarle.
    Se la sessione è ancora valida aggiorna l'ora dell'ultima attività.
    """
    adesso = int(time.time())
    entrato_il, ultima_attivita = session.get("entrato_il", 0), session.get("ultima_attivita", 0)
    if adesso - entrato_il > DURATA_MASSIMA_SECONDI or adesso - ultima_attivita > INATTIVITA_MASSIMA_SECONDI:
        return True
    session["ultima_attivita"] = adesso
    return False


def sessione_valida(utente: Utente | None) -> bool:
    """
    Returns: True se l'utente esiste, è attivo e la password non è cambiata dopo l'apertura della sessione.
    """
    if utente is None or not utente.attivo:
        return False
    return hmac.compare_digest(session.get("impronta", ""), impronta_password(utente.password_hash))
