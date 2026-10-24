from functools import wraps

from flask import abort, current_app, make_response, request

from app.db import ottieni_connessione
from app.servizi.tentativi import TentativiService


def limita_tentativi(ambito: str):
    """
    Decoratore delle rotte con una password da indovinare (login, cambio password): sui POST
    rifiuta con 429 chi ha già sbagliato 5 volte nell'ultimo minuto e registra come tentativo
    sbagliato ogni risposta 400. Chi entra al primo colpo non consuma il limite.
    L'IP è request.remote_addr, quello vero del visitatore anche dietro il proxy (PROXY_FIDATI).
    Si spegne con LIMITE_TENTATIVI_ATTIVO = False (solo nei test).
    """
    def decoratore(rotta):
        @wraps(rotta)
        def rotta_limitata(*args, **kwargs):
            if request.method != "POST" or not current_app.config["LIMITE_TENTATIVI_ATTIVO"]:
                return rotta(*args, **kwargs)
            servizio = TentativiService(ottieni_connessione(), current_app.secret_key)
            if servizio.bloccato(ambito, request.remote_addr):
                abort(429)
            risposta = make_response(rotta(*args, **kwargs))
            if risposta.status_code == 400:
                servizio.registra_fallito(ambito, request.remote_addr)
            return risposta
        return rotta_limitata
    return decoratore
