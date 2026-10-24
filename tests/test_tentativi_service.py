from datetime import datetime, timedelta

from app.servizi.tentativi import AMBITO_CAMBIO_PASSWORD, AMBITO_LOGIN, TentativiService

IP = "203.0.113.7"
INIZIO = datetime(2026, 10, 24, 18, 0, 0)


def _servizio(connessione) -> TentativiService:
    return TentativiService(connessione, "chiave-solo-per-i-test")


def _registra(servizio, volte, ambito=AMBITO_LOGIN, ip=IP, dal=INIZIO):
    for secondi in range(volte):
        servizio.registra_fallito(ambito, ip, dal + timedelta(seconds=secondi))


def test_quattro_errori_non_bloccano(connessione):
    servizio = _servizio(connessione)
    _registra(servizio, 4)
    assert not servizio.bloccato(AMBITO_LOGIN, IP, INIZIO + timedelta(seconds=5))


def test_cinque_errori_bloccano(connessione):
    servizio = _servizio(connessione)
    _registra(servizio, 5)
    assert servizio.bloccato(AMBITO_LOGIN, IP, INIZIO + timedelta(seconds=5))


def test_blocco_finisce_dopo_un_minuto(connessione):
    # Errori alle 18:00:00-18:00:04: alle 18:01:00 il primo conta ancora, alle 18:01:01 è uscito.
    servizio = _servizio(connessione)
    _registra(servizio, 5)
    assert servizio.bloccato(AMBITO_LOGIN, IP, INIZIO + timedelta(seconds=60))
    assert not servizio.bloccato(AMBITO_LOGIN, IP, INIZIO + timedelta(seconds=61))


def test_ambiti_e_indirizzi_separati(connessione):
    servizio = _servizio(connessione)
    _registra(servizio, 5)
    adesso = INIZIO + timedelta(seconds=5)
    assert not servizio.bloccato(AMBITO_CAMBIO_PASSWORD, IP, adesso)
    assert not servizio.bloccato(AMBITO_LOGIN, "198.51.100.1", adesso)


def test_ip_non_salvato_in_chiaro(connessione):
    servizio = _servizio(connessione)
    servizio.registra_fallito(AMBITO_LOGIN, IP, INIZIO)
    with connessione.cursor() as cur:
        cur.execute("SELECT impronta_ip FROM tentativi_accesso")
        impronte = [riga[0] for riga in cur.fetchall()]
    assert impronte == [servizio.impronta(IP)]
    assert IP not in impronte[0] and len(impronte[0]) == 64
    # Con un'altra SECRET_KEY la stessa impronta non si ricalcola.
    assert TentativiService(connessione, "altra-chiave").impronta(IP) != impronte[0]


def test_tentativi_vecchi_cancellati(connessione):
    servizio = _servizio(connessione)
    _registra(servizio, 3)
    servizio.registra_fallito(AMBITO_LOGIN, "198.51.100.1", INIZIO + timedelta(hours=1, seconds=3))
    with connessione.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM tentativi_accesso")
        assert cur.fetchone()[0] == 1
