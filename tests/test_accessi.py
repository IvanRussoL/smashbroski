import pytest
from flask import url_for

from app import create_app
from app.servizi.tentativi import FINESTRA, LIMITE_TENTATIVI
from conftest import configurazione_test

EMAIL, PASSWORD = "proprietario@example.com", "password-dei-test-123"


def rotte_proprietario(app):
    """
    Tutte le rotte registrate con prefisso /proprietario, con un indirizzo di esempio e un metodo:
    una rotta aggiunta in futuro finisce qui da sola.
    """
    rotte = []
    with app.test_request_context():
        for regola in app.url_map.iter_rules():
            if not regola.rule.startswith("/proprietario"):
                continue
            indirizzo = url_for(regola.endpoint, **{argomento: 1 for argomento in regola.arguments})
            metodo = "GET" if "GET" in regola.methods else "POST"
            rotte.append((metodo, indirizzo))
    return rotte


def test_rotte_proprietario_anonimo_redirect(app, client):
    rotte = rotte_proprietario(app)
    assert len(rotte) >= 5
    for metodo, indirizzo in rotte:
        risposta = client.open(indirizzo, method=metodo)
        assert risposta.status_code == 302, indirizzo
        assert risposta.headers["Location"].endswith("/auth/login"), indirizzo


def test_rotte_proprietario_autenticato(client_proprietario):
    assert client_proprietario.get("/proprietario/").status_code == 200
    assert client_proprietario.get("/proprietario/orari").status_code == 200


def test_account_disattivato_perde_accesso(client_proprietario, database_modificato):
    assert client_proprietario.get("/proprietario/").status_code == 200
    with database_modificato.cursor() as cur:
        cur.execute("UPDATE utenti SET attivo = FALSE WHERE email = %s", (EMAIL,))
    database_modificato.commit()
    risposta = client_proprietario.get("/proprietario/")
    assert risposta.headers["Location"].endswith("/auth/login")
    with client_proprietario.session_transaction() as sessione:
        assert "utente_id" not in sessione


def test_login_corretto(client):
    risposta = client.post("/auth/login", data={"email": EMAIL, "password": PASSWORD})
    assert risposta.status_code == 302
    assert risposta.headers["Location"].endswith("/proprietario/")
    assert client.get("/proprietario/").status_code == 200


def test_login_sessione_solo_id(client):
    with client.session_transaction() as sessione:
        sessione["valore_precedente"] = "da cancellare"
    client.post("/auth/login", data={"email": EMAIL, "password": PASSWORD})
    with client.session_transaction() as sessione:
        assert sessione["utente_id"] == 1
        assert set(sessione.keys()) <= {"utente_id", "impronta", "entrato_il", "ultima_attivita", "_permanent"}
        assert len(sessione["impronta"]) == 64 and "argon2" not in sessione["impronta"]


def test_login_messaggio_generico(client):
    password_errata = client.post("/auth/login", data={"email": EMAIL, "password": "sbagliata-sbagliata"})
    email_inesistente = client.post("/auth/login", data={"email": "nessuno@example.com", "password": PASSWORD})
    assert password_errata.status_code == email_inesistente.status_code == 400
    for risposta in (password_errata, email_inesistente):
        assert "Email o password non corretti." in risposta.get_data(as_text=True)


def test_logout_solo_post(client_proprietario):
    assert client_proprietario.get("/auth/logout").status_code == 405
    risposta = client_proprietario.post("/auth/logout")
    assert risposta.status_code == 302
    with client_proprietario.session_transaction() as sessione:
        assert "utente_id" not in sessione
    assert client_proprietario.get("/proprietario/").status_code == 302


def test_csrf_post_senza_token(database_di_prova):
    app = create_app(configurazione_test(WTF_CSRF_ENABLED=True))
    client = app.test_client()
    with client.session_transaction() as sessione:
        sessione["utente_id"] = 1
    for indirizzo in ("/auth/logout", "/proprietario/voci/nuova?categoria=3",
                      "/proprietario/voci/1/visibilita", "/proprietario/orari", "/proprietario/password",
                      "/auth/login"):
        risposta = client.post(indirizzo, data={"attiva": "0"})
        assert risposta.status_code == 400, indirizzo
        assert "Modulo scaduto o non valido" in risposta.get_data(as_text=True)


def test_login_avvisa_del_limite_di_tentativi(client):
    pagina = client.get("/auth/login").get_data(as_text=True)
    # La nota deve dire lo stesso numero e la stessa durata del limite configurato.
    assert (LIMITE_TENTATIVI, FINESTRA.total_seconds()) == (5, 60)
    assert "Dopo 5 tentativi sbagliati l'accesso si blocca per un minuto" in pagina
    assert 'aria-describedby="nota-tentativi"' in pagina


def _conta_tentativi(connessione) -> int:
    with connessione.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM tentativi_accesso")
        return cur.fetchone()[0]


def test_rate_limit_login(database_modificato):
    # database_modificato: i tentativi restano nel database di prova e a fine test viene ricaricato.
    client = create_app(configurazione_test(LIMITE_TENTATIVI_ATTIVO=True)).test_client()
    for _ in range(5):
        assert client.post("/auth/login", data={"email": EMAIL, "password": "sbagliata"}).status_code == 400
    risposta = client.post("/auth/login", data={"email": EMAIL, "password": "sbagliata"})
    assert risposta.status_code == 429
    assert "Troppi tentativi" in risposta.get_data(as_text=True)
    # Bloccata anche la password giusta, come dice la nota sotto "Entra".
    assert client.post("/auth/login", data={"email": EMAIL, "password": PASSWORD}).status_code == 429
    # Le richieste rifiutate con 429 non allungano il blocco.
    assert _conta_tentativi(database_modificato) == 5


def test_rate_limit_login_riuscito_non_conta(database_modificato):
    client = create_app(configurazione_test(LIMITE_TENTATIVI_ATTIVO=True)).test_client()
    for _ in range(6):
        assert client.post("/auth/login", data={"email": EMAIL, "password": PASSWORD}).status_code == 302
    assert _conta_tentativi(database_modificato) == 0


def test_rate_limit_condiviso_fra_processi(database_modificato):
    """
    Due app create a parte sono come due processi del server: con il conteggio in memoria ognuna
    avrebbe i suoi 5 tentativi, con il database il limite è unico.
    """
    primo = create_app(configurazione_test(LIMITE_TENTATIVI_ATTIVO=True)).test_client()
    secondo = create_app(configurazione_test(LIMITE_TENTATIVI_ATTIVO=True)).test_client()
    sbagliato = {"email": EMAIL, "password": "sbagliata"}
    for client in (primo, secondo, primo, secondo, primo):
        assert client.post("/auth/login", data=sbagliato).status_code == 400
    assert secondo.post("/auth/login", data=sbagliato).status_code == 429
    assert primo.post("/auth/login", data=sbagliato).status_code == 429


def test_cache_no_store_area_riservata(client_proprietario):
    for indirizzo in ("/proprietario/", "/proprietario/orari", "/proprietario/voci/1"):
        assert client_proprietario.get(indirizzo).headers["Cache-Control"] == "no-store"


@pytest.mark.parametrize("produzione", [False, True])
def test_cookie_sessione_attributi(database_di_prova, produzione):
    client = create_app(configurazione_test(PRODUZIONE=produzione)).test_client()
    risposta = client.post("/auth/login", data={"email": EMAIL, "password": PASSWORD})
    cookie = risposta.headers["Set-Cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert ("Secure" in cookie) is produzione


def test_rate_limit_cambio_password(database_modificato):
    client = create_app(configurazione_test(LIMITE_TENTATIVI_ATTIVO=True)).test_client()
    assert client.post("/auth/login", data={"email": EMAIL, "password": PASSWORD}).status_code == 302
    dati = {"attuale": "sbagliata", "nuova": "nuova-password-dei-test", "conferma": "nuova-password-dei-test"}
    for _ in range(5):
        assert client.post("/proprietario/password", data=dati).status_code == 400
    assert client.post("/proprietario/password", data=dati).status_code == 429



def test_richiesta_troppo_grande_rifiutata(client):
    risposta = client.post("/auth/login", data={"email": EMAIL, "password": "x" * 70_000})
    assert risposta.status_code == 413
    assert "Dati inviati troppo grandi." in risposta.get_data(as_text=True)


@pytest.mark.parametrize("proxy, ip_atteso", [(0, "127.0.0.1"), (1, "203.0.113.7")])
def test_ip_del_visitatore_dietro_proxy(database_di_prova, proxy, ip_atteso):
    """
    Senza proxy dichiarati X-Forwarded-For si ignora (chiunque potrebbe scriverlo); con un proxy
    l'IP che conta i tentativi di login è quello del visitatore, non quello del proxy.
    """
    from flask import request

    app = create_app(configurazione_test(PROXY_FIDATI=proxy))
    app.add_url_rule("/ip-di-prova", "ip_di_prova", lambda: request.remote_addr)
    risposta = app.test_client().get("/ip-di-prova", headers={"X-Forwarded-For": "203.0.113.7"})
    assert risposta.get_data(as_text=True) == ip_atteso


def test_sessione_vecchia_non_basta(client):
    # Una sessione con il solo id (per esempio di prima di questa versione) non apre l'area.
    with client.session_transaction() as sessione:
        sessione["utente_id"] = 1
    assert client.get("/proprietario/").headers["Location"].endswith("/auth/login")


def test_cambio_password_chiude_le_altre_sessioni(app, database_modificato):
    telefono, computer = app.test_client(), app.test_client()
    for dispositivo in (telefono, computer):
        assert dispositivo.post("/auth/login", data={"email": EMAIL, "password": PASSWORD}).status_code == 302
    risposta = telefono.post("/proprietario/password", data={
        "attuale": PASSWORD, "nuova": "nuova-password-dei-test", "conferma": "nuova-password-dei-test",
    })
    assert risposta.status_code == 302
    assert telefono.get("/proprietario/").status_code == 200  # chi l'ha cambiata resta dentro
    risposta = computer.get("/proprietario/")
    assert risposta.headers["Location"].endswith("/auth/login")  # l'altro dispositivo esce subito
    with computer.session_transaction() as sessione:
        assert "utente_id" not in sessione


def test_reimposta_password_chiude_le_sessioni(app, client_proprietario, database_modificato):
    risultato = app.test_cli_runner().invoke(
        args=["reimposta-password"], input=f"{EMAIL}\nreimpostata-dallo-sviluppatore\nreimpostata-dallo-sviluppatore\n",
    )
    assert risultato.exit_code == 0, risultato.output
    assert client_proprietario.get("/proprietario/").headers["Location"].endswith("/auth/login")


def _sposta_indietro(client, chiave, secondi):
    with client.session_transaction() as sessione:
        sessione[chiave] -= secondi


@pytest.mark.parametrize("chiave, secondi", [
    ("ultima_attivita", 60 * 60 + 1),       # più di un'ora senza attività
    ("entrato_il", 8 * 60 * 60 + 1),        # più di 8 ore dal login, anche se attivo
])
def test_sessione_scaduta(client_proprietario, chiave, secondi):
    _sposta_indietro(client_proprietario, chiave, secondi)
    risposta = client_proprietario.get("/proprietario/")
    assert risposta.headers["Location"].endswith("/auth/login")
    pagina = client_proprietario.get("/auth/login").get_data(as_text=True)
    assert "Sessione scaduta" in pagina
    with client_proprietario.session_transaction() as sessione:
        assert "utente_id" not in sessione


def test_attivita_rinnova_il_timeout_di_inattivita(client_proprietario):
    _sposta_indietro(client_proprietario, "ultima_attivita", 50 * 60)
    assert client_proprietario.get("/proprietario/").status_code == 200
    _sposta_indietro(client_proprietario, "ultima_attivita", 50 * 60)  # 50 minuti dall'ultima pagina, non 100
    assert client_proprietario.get("/proprietario/").status_code == 200
