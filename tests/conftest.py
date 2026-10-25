import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from app import create_app
from app.db import crea_connessione
from app.servizi.auth import AuthService

load_dotenv()

CARTELLA_DATABASE = Path(__file__).resolve().parent.parent / "database"

# Tutti i test usano il database di prova, anche le richieste inviate all'app.
# CSRF e limite dei tentativi di login sono spenti, tranne nei test che li verificano.
CONFIGURAZIONE_TEST = {
    "TESTING": True,
    "SECRET_KEY": "chiave-solo-per-i-test",
    "DB_NAME": os.environ.get("DB_NAME_TEST"),
    "WTF_CSRF_ENABLED": False,
    "LIMITE_TENTATIVI_ATTIVO": False,
}



def configurazione_test(**modifiche) -> dict:
    """
    Configurazione di test con alcuni valori cambiati (es. CSRF o limite dei tentativi accesi).
    """
    return {**CONFIGURAZIONE_TEST, **modifiche}


# Proprietario presente nel database di prova (sezione 1.3 del piano di test).
EMAIL_PROPRIETARIO = "proprietario@example.com"
PASSWORD_PROPRIETARIO = "password-dei-test-123"


def esegui_file_sql(connessione, percorso: Path) -> None:
    """
    Esegue uno dopo l'altro gli statement di un file SQL e conferma con commit.
    Le righe che iniziano con "--" sono commenti e vengono saltate; gli statement sono separati
    da ";" (nei file del progetto il ";" non compare dentro i testi).
    """
    righe = [
        riga for riga in percorso.read_text(encoding="utf-8-sig").splitlines()
        if not riga.strip().startswith("--")
    ]
    statement = [s.strip() for s in "\n".join(righe).split(";") if s.strip()]
    with connessione.cursor() as cur:
        for sql in statement:
            cur.execute(sql)
    connessione.commit()


@pytest.fixture(scope="session")
def database_di_prova():
    """
    Una volta per esecuzione di pytest: ricrea le tabelle del database di prova con schema.sql
    e carica dati_iniziali.sql. Si rifiuta di partire se il nome non finisce con "_test",
    per non cancellare mai il database di sviluppo.
    """
    configurazione = create_app(CONFIGURAZIONE_TEST).config
    nome = configurazione["DB_NAME"]
    if not nome or not nome.endswith("_test"):
        raise RuntimeError(f"DB_NAME_TEST deve indicare un database che finisce con _test, non {nome!r}.")
    connessione = crea_connessione(configurazione)
    prepara_database(connessione)
    connessione.close()


def prepara_database(connessione) -> None:
    """
    Ricrea le tabelle, carica i dati iniziali e crea il proprietario di prova, con commit.
    """
    esegui_file_sql(connessione, CARTELLA_DATABASE / "schema.sql")
    esegui_file_sql(connessione, CARTELLA_DATABASE / "dati_iniziali.sql")
    AuthService(connessione).crea_proprietario(EMAIL_PROPRIETARIO, PASSWORD_PROPRIETARIO)


@pytest.fixture
def app():
    """
    App creata con la configurazione di test, indipendente da SECRET_KEY e DB_NAME di .env.
    """
    return create_app(CONFIGURAZIONE_TEST)


class ConnessioneDiTest:
    """
    Connessione vera al database di prova, ma commit() non conferma niente: i servizi possono
    chiamarlo come in produzione e a fine test il rollback annulla tutto.
    Le altre chiamate (cursor, rollback, ...) passano alla connessione vera.
    """

    def __init__(self, connessione):
        self._conn = connessione

    def commit(self) -> None:
        pass

    def __getattr__(self, nome):
        return getattr(self._conn, nome)


@pytest.fixture
def connessione(app, database_di_prova):
    """
    Connessione al database di prova per un test; a fine test tutte le modifiche vengono annullate,
    anche quelle che un servizio ha "confermato", così un test non lascia tracce per il successivo.
    """
    conn = crea_connessione(app.config)
    yield ConnessioneDiTest(conn)
    conn.rollback()
    conn.close()


@pytest.fixture
def client(app, database_di_prova):
    """
    Client che simula il browser: invia richieste all'app senza avviare il server.
    L'app usa la sua connessione al database di prova.
    """
    return app.test_client()


@pytest.fixture
def database_modificato(app, database_di_prova):
    """
    Connessione con commit veri, per i test che cambiano i dati e poi li guardano attraverso le
    pagine (l'app usa una connessione sua e vede solo i dati confermati). A fine test il database
    di prova viene ricaricato da schema e dati iniziali.
    """
    conn = crea_connessione(app.config)
    yield conn
    conn.rollback()
    prepara_database(conn)
    conn.close()


@pytest.fixture
def client_proprietario(client):
    """
    Client già entrato nell'area riservata come proprietario di prova, passando dal login vero
    (la sessione deve avere anche l'impronta della password).
    """
    risposta = client.post("/auth/login", data={"email": EMAIL_PROPRIETARIO, "password": PASSWORD_PROPRIETARIO})
    assert risposta.status_code == 302
    return client
