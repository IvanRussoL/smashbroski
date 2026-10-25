from datetime import UTC, datetime, timedelta

import pyotp
import pytest

from app import create_app
from app.eccezioni import DatiNonValidiError
from app.repository.utente import UtenteRepository
from app.servizi.due_passaggi import DuePassaggiService, codice_qr_svg
from conftest import EMAIL_PROPRIETARIO, PASSWORD_PROPRIETARIO, configurazione_test

CHIAVE = "chiave-solo-per-i-test"  # la SECRET_KEY dei test
ADESSO = datetime(2026, 10, 25, 14, 0, 0, tzinfo=UTC)


def _utente(connessione):
    return UtenteRepository(connessione).leggi_per_email(EMAIL_PROPRIETARIO)


def _segreto(connessione) -> str:
    return DuePassaggiService(connessione, CHIAVE).attivazione_in_corso(_utente(connessione).id)[1]


def _attiva(connessione, adesso=ADESSO) -> list[str]:
    servizio = DuePassaggiService(connessione, CHIAVE)
    utente_id = _utente(connessione).id
    servizio.prepara(utente_id)
    codice = pyotp.TOTP(_segreto(connessione)).at(adesso)
    return servizio.conferma(utente_id, codice, adesso)


# --- DuePassaggiService ---

def test_prepara_segreto_cifrato_e_non_ancora_attivo(connessione):
    servizio = DuePassaggiService(connessione, CHIAVE)
    servizio.prepara(_utente(connessione).id)
    utente = _utente(connessione)
    uri, segreto = servizio.attivazione_in_corso(utente.id)
    assert uri.startswith("otpauth://totp/") and "issuer=SmashBroski%20Pompei" in uri
    assert len(segreto) == 32  # 160 bit in base32
    assert not utente.totp_attivo
    assert segreto not in utente.totp_segreto  # nel database solo cifrato


def test_conferma_con_codice_sbagliato(connessione):
    servizio = DuePassaggiService(connessione, CHIAVE)
    servizio.prepara(_utente(connessione).id)
    with pytest.raises(DatiNonValidiError):
        servizio.conferma(_utente(connessione).id, "000000", ADESSO)
    assert not _utente(connessione).totp_attivo


def test_conferma_attiva_e_da_10_codici_di_riserva(connessione):
    codici = _attiva(connessione)
    assert len(codici) == 10 and len(set(codici)) == 10
    assert all(len(c) == 11 and c[5] == "-" for c in codici)
    assert _utente(connessione).totp_attivo
    with connessione.cursor() as cur:
        cur.execute("SELECT codice_hash FROM codici_riserva")
        hash_salvati = [riga[0] for riga in cur.fetchall()]
    assert all(h.startswith("$argon2id$") for h in hash_salvati)
    assert not any(c.replace("-", "") in h for c in codici for h in hash_salvati)


def test_prepara_rifiutato_se_gia_attiva(connessione):
    _attiva(connessione)
    with pytest.raises(DatiNonValidiError):
        DuePassaggiService(connessione, CHIAVE).prepara(_utente(connessione).id)


def test_codice_valido_una_volta_sola(connessione):
    _attiva(connessione)
    servizio = DuePassaggiService(connessione, CHIAVE)
    totp = pyotp.TOTP(DuePassaggiService(connessione, CHIAVE)._decifra(_utente(connessione).totp_segreto))
    dopo = ADESSO + timedelta(seconds=60)
    codice = totp.at(dopo)
    assert servizio.verifica(_utente(connessione), codice, dopo)
    assert not servizio.verifica(_utente(connessione), codice, dopo)  # lo stesso codice non vale due volte


def test_finestra_di_un_intervallo(connessione):
    _attiva(connessione)
    servizio = DuePassaggiService(connessione, CHIAVE)
    totp = pyotp.TOTP(servizio._decifra(_utente(connessione).totp_segreto))
    adesso = ADESSO + timedelta(minutes=10)
    assert not servizio.verifica(_utente(connessione), totp.at(adesso - timedelta(seconds=90)), adesso)
    assert servizio.verifica(_utente(connessione), totp.at(adesso - timedelta(seconds=30)), adesso)


def test_codice_di_riserva_una_volta_sola(connessione):
    codici = _attiva(connessione)
    servizio = DuePassaggiService(connessione, CHIAVE)
    # Si può scrivere in maiuscolo, con spazi o senza trattino.
    assert servizio.verifica(_utente(connessione), " " + codici[0].upper().replace("-", " "), ADESSO)
    assert not servizio.verifica(_utente(connessione), codici[0], ADESSO)
    assert servizio.codici_riserva_rimasti(_utente(connessione).id) == 9


def test_rigenera_codici_annulla_i_vecchi(connessione):
    vecchi = _attiva(connessione)
    servizio = DuePassaggiService(connessione, CHIAVE)
    nuovi = servizio.rigenera_codici_riserva(_utente(connessione).id)
    assert not servizio.verifica(_utente(connessione), vecchi[0], ADESSO)
    assert servizio.verifica(_utente(connessione), nuovi[0], ADESSO)


def test_disattiva_cancella_segreto_e_codici(connessione):
    _attiva(connessione)
    DuePassaggiService(connessione, CHIAVE).disattiva(_utente(connessione).id)
    utente = _utente(connessione)
    assert not utente.totp_attivo and utente.totp_segreto is None
    assert DuePassaggiService(connessione, CHIAVE).codici_riserva_rimasti(utente.id) == 0


def test_secret_key_cambiata_chiede_di_riattivare(connessione):
    _attiva(connessione)
    with pytest.raises(DatiNonValidiError):
        DuePassaggiService(connessione, "altra-chiave").verifica(_utente(connessione), "123456", ADESSO)


def test_qr_senza_misure_fisse():
    svg = codice_qr_svg("otpauth://totp/prova?secret=ABC")
    assert svg.startswith('<svg role="img"') and "mm" not in svg.split(">", 1)[0]


# --- Pagine ---

def _codice_attuale(connessione, secondi=0) -> str:
    connessione.commit()  # vede i dati confermati dall'app
    segreto = DuePassaggiService(connessione, CHIAVE)._decifra(_utente(connessione).totp_segreto)
    return pyotp.TOTP(segreto).at(datetime.now(UTC) + timedelta(seconds=secondi))


def _attiva_dalla_pagina(client, connessione) -> list[str]:
    pagina = client.post("/proprietario/due-passaggi", data={"azione": "prepara"}).get_data(as_text=True)
    assert "<svg" in pagina and "Codice di 6 cifre" in pagina
    pagina = client.post("/proprietario/due-passaggi", data={
        "azione": "conferma", "codice": _codice_attuale(connessione),
    }).get_data(as_text=True)
    assert "Codici di riserva" in pagina and "è <strong>attiva</strong>" in pagina
    connessione.commit()
    return pagina


def test_attivazione_e_accesso_con_codice(client_proprietario, database_modificato, app):
    _attiva_dalla_pagina(client_proprietario, database_modificato)
    client = app.test_client()
    risposta = client.post("/auth/login", data={"email": EMAIL_PROPRIETARIO, "password": PASSWORD_PROPRIETARIO})
    assert risposta.headers["Location"].endswith("/auth/codice")
    # Password giusta ma senza codice: l'area resta chiusa.
    assert client.get("/proprietario/").headers["Location"].endswith("/auth/login")
    client.post("/auth/login", data={"email": EMAIL_PROPRIETARIO, "password": PASSWORD_PROPRIETARIO})
    risposta = client.post("/auth/codice", data={"codice": "000000"})
    assert risposta.status_code == 400 and "Il codice non è corretto o è scaduto." in risposta.get_data(as_text=True)
    # Il codice dell'intervallo dopo: quello attuale è già stato usato per l'attivazione.
    risposta = client.post("/auth/codice", data={"codice": _codice_attuale(database_modificato, 30)})
    assert risposta.headers["Location"].endswith("/proprietario/")
    assert client.get("/proprietario/").status_code == 200


def test_accesso_con_codice_di_riserva(client_proprietario, database_modificato, app):
    pagina = _attiva_dalla_pagina(client_proprietario, database_modificato)
    codice = pagina.split("<li><code>", 1)[1].split("</code>", 1)[0]
    client = app.test_client()
    client.post("/auth/login", data={"email": EMAIL_PROPRIETARIO, "password": PASSWORD_PROPRIETARIO})
    assert client.post("/auth/codice", data={"codice": codice}).headers["Location"].endswith("/proprietario/")


def test_codice_dopo_5_minuti_si_riparte_dalla_password(client_proprietario, database_modificato, app):
    _attiva_dalla_pagina(client_proprietario, database_modificato)
    client = app.test_client()
    client.post("/auth/login", data={"email": EMAIL_PROPRIETARIO, "password": PASSWORD_PROPRIETARIO})
    with client.session_transaction() as sessione:
        sessione["in_attesa_dal"] -= 301
    risposta = client.post("/auth/codice", data={"codice": _codice_attuale(database_modificato, 30)})
    assert risposta.headers["Location"].endswith("/auth/login")


def test_pagina_codice_senza_password_rimanda_al_login(client):
    assert client.get("/auth/codice").headers["Location"].endswith("/auth/login")


def test_codice_sbagliato_conta_i_tentativi(client_proprietario, database_modificato):
    _attiva_dalla_pagina(client_proprietario, database_modificato)
    client = create_app(configurazione_test(LIMITE_TENTATIVI_ATTIVO=True)).test_client()
    client.post("/auth/login", data={"email": EMAIL_PROPRIETARIO, "password": PASSWORD_PROPRIETARIO})
    for _ in range(5):
        assert client.post("/auth/codice", data={"codice": "000000"}).status_code == 400
    assert client.post("/auth/codice", data={"codice": "000000"}).status_code == 429


def test_togliere_la_verifica_chiede_la_password(client_proprietario, database_modificato):
    _attiva_dalla_pagina(client_proprietario, database_modificato)
    risposta = client_proprietario.post("/proprietario/due-passaggi", data={"azione": "disattiva", "password": "sbagliata"})
    assert risposta.status_code == 400 and "La password attuale non è corretta." in risposta.get_data(as_text=True)
    risposta = client_proprietario.post("/proprietario/due-passaggi", data={
        "azione": "disattiva", "password": PASSWORD_PROPRIETARIO,
    })
    assert risposta.status_code == 302
    database_modificato.commit()
    assert not _utente(database_modificato).totp_attivo


def test_comando_disattiva_due_passaggi(app, client_proprietario, database_modificato):
    _attiva_dalla_pagina(client_proprietario, database_modificato)
    risultato = app.test_cli_runner().invoke(args=["disattiva-due-passaggi", EMAIL_PROPRIETARIO])
    assert risultato.exit_code == 0, risultato.output
    database_modificato.commit()
    assert not _utente(database_modificato).totp_attivo


@pytest.mark.parametrize("indirizzo", ["/auth/login", "/auth/codice", "/proprietario/"])
def test_pagine_riservate_non_indicizzate(client, indirizzo):
    assert client.get(indirizzo).headers["X-Robots-Tag"] == "noindex, nofollow"


def test_pagine_pubbliche_indicizzate(client):
    assert "X-Robots-Tag" not in client.get("/").headers
