from app.db import ottieni_connessione


def test_connessione_al_database_di_prova(connessione):
    with connessione.cursor() as cur:
        cur.execute("SELECT DATABASE()")
        (nome,) = cur.fetchone()
    assert nome.endswith("_test")


def test_dati_iniziali_caricati(connessione):
    attesi = {
        "impostazioni": 1,
        "orari_settimanali": 10,
        "categorie": 7,
        "formati_prezzo": 10,
        "voci_menu": 25,
        "prezzi_voce": 50,
    }
    trovati = {}
    with connessione.cursor() as cur:
        for tabella in attesi:
            # Nome della tabella preso dal dizionario qui sopra, non da un dato esterno.
            cur.execute(f"SELECT COUNT(*) FROM {tabella}")
            (trovati[tabella],) = cur.fetchone()
    assert trovati == attesi


def test_una_connessione_per_richiesta_chiusa_alla_fine(app, database_di_prova):
    with app.app_context():
        prima = ottieni_connessione()
        seconda = ottieni_connessione()
        assert prima is seconda
        assert prima.is_connected()
    assert not prima.is_connected()
