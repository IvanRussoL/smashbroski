import mysql.connector
from flask import current_app, g


def crea_connessione(configurazione):
    """
    Apre una nuova connessione a MySQL con i parametri della configurazione dell'app
    (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME).
    Serve anche fuori da una richiesta: comandi da terminale e test.
    Returns: la connessione aperta, con autocommit spento (ogni modifica va confermata con commit).
    Raises: mysql.connector.Error se la connessione fallisce.
    """
    return mysql.connector.connect(
        host=configurazione["DB_HOST"],
        port=configurazione["DB_PORT"],
        user=configurazione["DB_USER"],
        password=configurazione["DB_PASSWORD"],
        database=configurazione["DB_NAME"],
    )


def ottieni_connessione():
    """
    Restituisce la connessione della richiesta in corso, aprendola al primo uso:
    una sola connessione per richiesta, condivisa da tutti i repository.
    Returns: la connessione salvata in g.
    """
    if "connessione" not in g:
        g.connessione = crea_connessione(current_app.config)
    return g.connessione


def chiudi_connessione(errore=None):
    """
    A fine richiesta annulla le modifiche senza commit e chiude la connessione.
    Flask la chiama da solo (registrata con teardown_appcontext in create_app).
    Args: errore, l'eccezione che ha interrotto la richiesta (la passa Flask), oppure None.
    """
    connessione = g.pop("connessione", None)
    if connessione is not None:
        connessione.rollback()
        connessione.close()
