import pytest

from app.eccezioni import DatiNonValidiError, NonTrovatoError
from app.servizi.menu import DatiVoce, MenuService, converti_prezzo

# Id dei dati iniziali (database/dati_iniziali.sql)
STARTERS, SALAD, BURGER, KIDS_MENU, SOFT_DRINKS, BEERS = 1, 2, 3, 4, 5, 6
SINGLE_SALAD = 3
PANINO_SINGLE, PANINO_DOUBLE, MENU_SINGLE = 5, 6, 7
SMASH_BURGER = 6


class ContaQuery:
    """
    Avvolge la connessione di test e conta le query eseguite, per verificare che il menù
    si legga con un numero fisso di query.
    """

    def __init__(self, connessione):
        self._conn = connessione
        self.query = 0

    def cursor(self, *args, **kwargs):
        return _CursoreContato(self, self._conn.cursor(*args, **kwargs))

    def __getattr__(self, nome):
        return getattr(self._conn, nome)


class _CursoreContato:
    def __init__(self, contatore, cursore):
        self._contatore, self._cursore = contatore, cursore

    def execute(self, *args, **kwargs):
        self._contatore.query += 1
        return self._cursore.execute(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *errore):
        self._cursore.close()

    def __getattr__(self, nome):
        return getattr(self._cursore, nome)


def nomi_voci(categorie, categoria_id):
    return [v.nome for c in categorie if c.id == categoria_id for v in c.voci]


# --- Conversione dei prezzi ---

@pytest.mark.parametrize("testo, centesimi", [
    ("7", 700), ("7,5", 750), ("7,50", 750), ("0,01", 1), ("999,99", 99999), (" 12,00 ", 1200),
])
def test_converti_prezzo_validi(testo, centesimi):
    assert converti_prezzo(testo) == centesimi


@pytest.mark.parametrize("testo", ["0", "0,00", "1000", "-1", "7,505", "7.50", "abc", "", "1.000,00"])
def test_converti_prezzo_non_validi(testo):
    with pytest.raises(DatiNonValidiError):
        converti_prezzo(testo)


# --- Menù pubblico ---

def test_menu_pubblico_categorie_in_ordine(connessione):
    categorie = MenuService(connessione).menu_pubblico()
    assert [c.nome for c in categorie] == [
        "Starters", "Salad", "Burger", "Kids Menù", "Soft Drinks", "Beers", "The Originals",
    ]


def test_menu_pubblico_25_voci_in_ordine_di_posizione(connessione):
    categorie = MenuService(connessione).menu_pubblico()
    assert sum(len(c.voci) for c in categorie) == 25
    for categoria in categorie:
        assert all(v.categoria_id == categoria.id for v in categoria.voci)
        assert [v.posizione for v in categoria.voci] == sorted(v.posizione for v in categoria.voci)


def test_starters_straccetti_prima_delle_patatine(connessione):
    # La voce con i formati 5 pz e 10 pz viene per prima, sotto l'intestazione delle colonne.
    assert nomi_voci(MenuService(connessione).menu_pubblico(), STARTERS) == [
        "Straccetti di pollo", "Patatine stick", "Patatine stick bacon & cheese",
    ]


def test_menu_pubblico_esclude_voci_nascoste(connessione):
    servizio = MenuService(connessione)
    servizio.imposta_visibilita(SMASH_BURGER, False)
    assert "Smash Burger" not in nomi_voci(servizio.menu_pubblico(), BURGER)
    assert "Smash Burger" in nomi_voci(servizio.menu_completo(), BURGER)


def test_menu_pubblico_esclude_categorie_senza_voci_visibili(connessione):
    servizio = MenuService(connessione)
    kids = [v.id for c in servizio.menu_completo() if c.id == KIDS_MENU for v in c.voci]
    for voce_id in kids:
        servizio.imposta_visibilita(voce_id, False)
    assert KIDS_MENU not in {c.id for c in servizio.menu_pubblico()}
    assert KIDS_MENU in {c.id for c in servizio.menu_completo()}  # l'area proprietario la vede
    servizio.imposta_visibilita(kids[0], True)
    assert KIDS_MENU in {c.id for c in servizio.menu_pubblico()}


def test_menu_pubblico_query_costanti(connessione):
    contatore = ContaQuery(connessione)
    servizio = MenuService(contatore)
    servizio.menu_pubblico()
    query_con_25_voci = contatore.query
    for numero in range(10):
        servizio.crea_voce(DatiVoce(SOFT_DRINKS, f"Bibita di prova {numero}", prezzo_unico="2"))
    contatore.query = 0
    categorie = servizio.menu_pubblico()
    assert sum(len(c.voci) for c in categorie) == 35
    assert contatore.query == query_con_25_voci


# --- Creazione ---

def test_crea_voce_prezzo_unico(connessione):
    servizio = MenuService(connessione)
    voce_id = servizio.crea_voce(DatiVoce(SOFT_DRINKS, "Aranciata 33cl", prezzo_unico="1,50"))
    voce = servizio.leggi_voce(voce_id)
    assert voce.ha_prezzo_unico() is True
    assert voce.prezzi[0].prezzo_centesimi == 150
    assert voce.posizione == 4  # in fondo alla categoria, dopo le 3 voci iniziali


def test_crea_voce_con_formati(connessione):
    servizio = MenuService(connessione)
    voce_id = servizio.crea_voce(DatiVoce(
        BURGER, "Smash Prova", descrizione="Hamburger, salsa smash",
        prezzi_formati=[(PANINO_SINGLE, "7,50"), (PANINO_DOUBLE, ""), (MENU_SINGLE, "10,50")],
    ))
    voce = servizio.leggi_voce(voce_id)
    assert [(p.etichetta_formato, p.prezzo_centesimi) for p in voce.prezzi] == [
        ("Panino single hamb.", 750), ("Menù single hamb.", 1050),
    ]


def test_crea_voce_prezzo_unico_in_categoria_con_formati(connessione):
    servizio = MenuService(connessione)
    voce_id = servizio.crea_voce(DatiVoce(STARTERS, "Onion rings", prezzo_unico="3,50"))
    assert servizio.leggi_voce(voce_id).ha_prezzo_unico() is True


def test_prezzo_unico_e_formati_insieme_errore(connessione):
    with pytest.raises(DatiNonValidiError):
        MenuService(connessione).crea_voce(
            DatiVoce(BURGER, "Doppio", prezzo_unico="7", prezzi_formati=[(PANINO_SINGLE, "7")])
        )


def test_formato_di_altra_categoria_errore(connessione):
    with pytest.raises(DatiNonValidiError):
        MenuService(connessione).crea_voce(DatiVoce(BURGER, "Burger", prezzi_formati=[(SINGLE_SALAD, "8")]))


def test_formato_in_categoria_senza_formati_errore(connessione):
    with pytest.raises(DatiNonValidiError):
        MenuService(connessione).crea_voce(DatiVoce(BEERS, "Peroni 33cl", prezzi_formati=[(PANINO_SINGLE, "3")]))


def test_formato_ripetuto_errore(connessione):
    with pytest.raises(DatiNonValidiError):
        MenuService(connessione).crea_voce(DatiVoce(
            BURGER, "Ripetuto", prezzi_formati=[(PANINO_SINGLE, "7"), (PANINO_SINGLE, "8")],
        ))


def test_voce_senza_prezzi_errore(connessione):
    with pytest.raises(DatiNonValidiError):
        MenuService(connessione).crea_voce(DatiVoce(BURGER, "Senza prezzo", prezzi_formati=[(PANINO_SINGLE, "")]))


@pytest.mark.parametrize("campi", [
    {"nome": ""}, {"nome": "   "}, {"nome": "x" * 101}, {"descrizione": "x" * 256},
])
def test_lunghezze_massime(connessione, campi):
    dati = DatiVoce(SOFT_DRINKS, "Bibita", prezzo_unico="2")
    for nome, valore in campi.items():
        setattr(dati, nome, valore)
    with pytest.raises(DatiNonValidiError):
        MenuService(connessione).crea_voce(dati)


def test_nome_duplicato_nella_categoria_errore(connessione):
    with pytest.raises(DatiNonValidiError) as errore:
        MenuService(connessione).crea_voce(DatiVoce(BURGER, "smash burger", prezzi_formati=[(PANINO_SINGLE, "7")]))
    assert "c'è già una voce" in errore.value.messaggi[0]


def test_categoria_inesistente_errore(connessione):
    with pytest.raises(DatiNonValidiError):
        MenuService(connessione).crea_voce(DatiVoce(99, "Voce", prezzo_unico="2"))


def test_errori_raccolti_tutti_insieme(connessione):
    with pytest.raises(DatiNonValidiError) as errore:
        MenuService(connessione).crea_voce(DatiVoce(SOFT_DRINKS, "", posizione="zero", prezzo_unico="7.50"))
    assert len(errore.value.messaggi) == 3  # nome, posizione, prezzo


def test_errore_nessun_salvataggio_parziale(connessione):
    servizio = MenuService(connessione)
    with pytest.raises(DatiNonValidiError):
        servizio.crea_voce(DatiVoce(
            BURGER, "Mezzo salvato", prezzi_formati=[(PANINO_SINGLE, "7"), (MENU_SINGLE, "abc")],
        ))
    assert "Mezzo salvato" not in nomi_voci(servizio.menu_completo(), BURGER)
    with connessione.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM prezzi_voce")
        assert cur.fetchone()[0] == 50


# --- Modifica, visibilità ---

def test_modifica_sostituisce_prezzi(connessione):
    servizio = MenuService(connessione)
    servizio.modifica_voce(SMASH_BURGER, DatiVoce(
        BURGER, "Smash Burger", descrizione="Hamburger, insalata, pomodoro, salsa smash", posizione="1",
        prezzi_formati=[(PANINO_SINGLE, "7,20"), (MENU_SINGLE, "10")],
    ))
    voce = servizio.leggi_voce(SMASH_BURGER)
    assert [(p.formato_id, p.prezzo_centesimi) for p in voce.prezzi] == [(PANINO_SINGLE, 720), (MENU_SINGLE, 1000)]


def test_modifica_mantiene_il_proprio_nome_e_la_visibilita(connessione):
    servizio = MenuService(connessione)
    servizio.imposta_visibilita(SMASH_BURGER, False)
    servizio.modifica_voce(SMASH_BURGER, DatiVoce(
        BURGER, "SMASH BURGER", posizione="1", prezzi_formati=[(PANINO_SINGLE, "7")],
    ))
    voce = servizio.leggi_voce(SMASH_BURGER)
    assert (voce.nome, voce.attiva) == ("SMASH BURGER", False)


def test_nascondi_e_rimostra(connessione):
    servizio = MenuService(connessione)
    prima = servizio.leggi_voce(SMASH_BURGER)
    servizio.imposta_visibilita(SMASH_BURGER, False)
    assert servizio.leggi_voce(SMASH_BURGER).attiva is False
    servizio.imposta_visibilita(SMASH_BURGER, True)
    assert servizio.leggi_voce(SMASH_BURGER) == prima


def test_voce_inesistente(connessione):
    servizio = MenuService(connessione)
    with pytest.raises(NonTrovatoError):
        servizio.modifica_voce(99999, DatiVoce(BURGER, "Nessuna", prezzi_formati=[(PANINO_SINGLE, "7")]))
    with pytest.raises(NonTrovatoError):
        servizio.imposta_visibilita(99999, False)


def test_testo_con_apici_salvato_come_testo(connessione):
    servizio = MenuService(connessione)
    nome = "Bro's '; DROP TABLE voci_menu; --"
    voce_id = servizio.crea_voce(DatiVoce(BURGER, nome, prezzi_formati=[(PANINO_SINGLE, "7")]))
    assert servizio.leggi_voce(voce_id).nome == nome
    assert len(nomi_voci(servizio.menu_completo(), BURGER)) == 8  # la tabella esiste ancora


# --- Cambio di categoria ---

THE_ORIGINALS, BURGER_ORIGINALS, MENU_ORIGINALS = 7, 9, 10


def test_modifica_sposta_la_voce_in_altra_categoria(connessione):
    servizio = MenuService(connessione)
    servizio.modifica_voce(SMASH_BURGER, DatiVoce(
        THE_ORIGINALS, "Smash Burger", prezzi_formati=[(BURGER_ORIGINALS, "8"), (MENU_ORIGINALS, "12")],
    ))
    voce = servizio.leggi_voce(SMASH_BURGER)
    assert voce.categoria_id == THE_ORIGINALS
    assert voce.posizione == 6  # in fondo, dopo le 5 voci di The Originals
    assert [(p.etichetta_formato, p.prezzo_centesimi) for p in voce.prezzi] == [("Burger", 800), ("Menù", 1200)]
    assert "Smash Burger" not in nomi_voci(servizio.menu_pubblico(), BURGER)
    assert "Smash Burger" in nomi_voci(servizio.menu_pubblico(), THE_ORIGINALS)


def test_spostamento_con_i_formati_della_vecchia_categoria_errore(connessione):
    with pytest.raises(DatiNonValidiError):
        MenuService(connessione).modifica_voce(SMASH_BURGER, DatiVoce(
            THE_ORIGINALS, "Smash Burger", prezzi_formati=[(PANINO_SINGLE, "7")],
        ))


def test_spostamento_con_nome_gia_usato_nella_nuova_categoria_errore(connessione):
    with pytest.raises(DatiNonValidiError):
        MenuService(connessione).modifica_voce(SMASH_BURGER, DatiVoce(
            THE_ORIGINALS, "Scapece", prezzi_formati=[(BURGER_ORIGINALS, "8")],
        ))
