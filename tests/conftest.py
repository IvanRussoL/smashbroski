import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from app import create_app
from app.db import crea_connessione

load_dotenv()

CARTELLA_DATABASE = Path(__file__).resolve().parent.parent / "database"

# Tutti i test usano il database di prova, anche le richieste inviate all'app.
CONFIGURAZIONE_TEST = {
    "TESTING": True,
    "SECRET_KEY": "chiave-solo-per-i-test",
    "DB_NAME": os.environ.get("DB_NAME_TEST"),
}


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
    esegui_file_sql(connessione, CARTELLA_DATABASE / "schema.sql")
    esegui_file_sql(connessione, CARTELLA_DATABASE / "dati_iniziali.sql")
    connessione.close()


@pytest.fixture
def app():
    """
    App creata con la configurazione di test, indipendente da SECRET_KEY e DB_NAME di .env.
    """
    return create_app(CONFIGURAZIONE_TEST)


@pytest.fixture
def connessione(app, database_di_prova):
    """
    Connessione al database di prova per un test; a fine test le modifiche senza commit
    vengono annullate, così un test non lascia tracce per il successivo.
    """
    conn = crea_connessione(app.config)
    yield conn
    conn.rollback()
    conn.close()
