import pytest
from flask import url_for

from app import create_app
from app.limiti import limiter
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
        assert set(sessione.keys()) <= {"utente_id", "_permanent"}


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
                      "/proprietario/voci/1/visibilita", "/proprietario/orari", "/auth/login"):
        risposta = client.post(indirizzo, data={"attiva": "0"})
        assert risposta.status_code == 400, indirizzo
        assert "Modulo scaduto o non valido" in risposta.get_data(as_text=True)


def test_login_avvisa_del_limite_di_tentativi(client):
    from app.limiti import LIMITE_TENTATIVI_LOGIN
    pagina = client.get("/auth/login").get_data(as_text=True)
    # La nota deve dire lo stesso numero del limite configurato.
    assert LIMITE_TENTATIVI_LOGIN == "5 per minute"
    assert "Dopo 5 tentativi sbagliati l'accesso si blocca per un minuto" in pagina
    assert 'aria-describedby="nota-tentativi"' in pagina


def test_rate_limit_login(database_di_prova):
    app = create_app(configurazione_test(RATELIMIT_ENABLED=True))
    client = app.test_client()
    with app.app_context():
        limiter.reset()
    for _ in range(5):
        assert client.post("/auth/login", data={"email": EMAIL, "password": "sbagliata"}).status_code == 400
    risposta = client.post("/auth/login", data={"email": EMAIL, "password": "sbagliata"})
    assert risposta.status_code == 429
    assert "Troppi tentativi" in risposta.get_data(as_text=True)
    with app.app_context():
        limiter.reset()


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
