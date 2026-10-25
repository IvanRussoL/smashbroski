from functools import wraps

from flask import abort, current_app, g, make_response, request

from app.db import ottieni_connessione
from app.servizi.tentativi import TentativiService


def limita_tentativi(ambito: str):
    """
    Decoratore delle rotte con una password da indovinare (login, cambio password): sui POST
    rifiuta con 429 chi ha già sbagliato 5 volte nell'ultimo minuto e registra un tentativo
    sbagliato quando la rotta mette g.password_sbagliata = True. Chi entra al primo colpo, o
    sbaglia solo altri campi (es. la conferma della nuova password), non consuma il limite.
    Prima di chiamare la rotta mette in g.tentativi_rimasti quanti tentativi resteranno se
    questo è sbagliato, per mostrarlo nella pagina.
    L'IP è request.remote_addr, quello vero del visitatore anche dietro il proxy (PROXY_FIDATI).
    Si spegne con LIMITE_TENTATIVI_ATTIVO = False (solo nei test).
    """
    def decoratore(rotta):
        @wraps(rotta)
        def rotta_limitata(*args, **kwargs):
            if request.method != "POST" or not current_app.config["LIMITE_TENTATIVI_ATTIVO"]:
                return rotta(*args, **kwargs)
            servizio = TentativiService(ottieni_connessione(), current_app.secret_key)
            rimasti = servizio.rimasti(ambito, request.remote_addr)
            if rimasti == 0:
                abort(429)
            g.tentativi_rimasti = rimasti - 1
            risposta = make_response(rotta(*args, **kwargs))
            if g.get("password_sbagliata"):
                servizio.registra_fallito(ambito, request.remote_addr)
            return risposta
        return rotta_limitata
    return decoratore
