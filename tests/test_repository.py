from datetime import time

from app.modelli.menu import PrezzoVoce, VoceMenu
from app.modelli.orari import Turno
from app.modelli.utente import Utente
from app.repository.impostazioni import ImpostazioniRepository
from app.repository.menu import MenuRepository
from app.repository.orari import OrariRepository
from app.repository.utente import UtenteRepository

# Id dei dati iniziali (database/dati_iniziali.sql)
BURGER, SOFT_DRINKS, KIDS_MENU = 3, 5, 4
SMASH_BURGER, LOS_POLLOS_CLASSIC, PATATINE_STICK = 6, 11, 1
PANINO_SINGLE, MENU_SINGLE = 5, 7


# --- Impostazioni ---

def test_impostazioni_dati_iniziali(connessione):
    impostazioni = ImpostazioniRepository(connessione).leggi()
    assert impostazioni.nome_locale == "SmashBroski Pompei"
    assert impostazioni.indirizzo == "Vico dei Paninari, 7 - 80045 Pompei (NA)"
    assert impostazioni.telefono == "+390810000000"
    assert impostazioni.telefono_di_prova is True
    assert impostazioni.fuso_orario == "Europe/Rome"


# --- Orari ---

def test_turni_dati_iniziali_in_ordine_e_di_tipo_time(connessione):
    turni = OrariRepository(connessione).leggi_turni()
    assert len(turni) == 10
    assert (turni[0].giorno_settimana, turni[0].ora_inizio, turni[0].ora_fine) == (1, time(12, 0), time(15, 0))
    assert (turni[1].giorno_settimana, turni[1].ora_inizio, turni[1].ora_fine) == (1, time(18, 0), time(1, 0))
    assert 2 not in {turno.giorno_settimana for turno in turni}  # martedì chiuso
    assert turni[-1].supera_mezzanotte() is True  # domenica 18:00-02:00


def test_sostituisci_turni(connessione):
    repo = OrariRepository(connessione)
    repo.sostituisci_turni([Turno(3, time(19, 0), time(23, 30)), Turno(1, time(12, 0), time(14, 0))])
    turni = repo.leggi_turni()
    assert [(t.giorno_settimana, t.ora_inizio, t.ora_fine) for t in turni] == [
        (1, time(12, 0), time(14, 0)),
        (3, time(19, 0), time(23, 30)),
    ]


# --- Menù: lettura ---

def test_menu_categorie_in_ordine_con_formati(connessione):
    categorie = MenuRepository(connessione).leggi_menu()
    assert [c.slug for c in categorie] == [
        "starters", "salad", "burger", "kids-menu", "soft-drinks", "beers", "the-originals",
    ]
    burger = categorie[2]
    assert [f.etichetta for f in burger.formati] == [
        "Panino single hamb.", "Panino double hamb.", "Menù single hamb.", "Menù double hamb.",
    ]
    assert categorie[4].formati == []  # Soft Drinks: solo prezzi unici


def test_menu_25_voci_in_ordine_con_prezzi(connessione):
    categorie = MenuRepository(connessione).leggi_menu()
    assert sum(len(c.voci) for c in categorie) == 25
    burger = categorie[2]
    assert [v.nome for v in burger.voci][:2] == ["Smash Burger", "Smash Salad"]
    smash = burger.voci[0]
    assert [(p.etichetta_formato, p.prezzo_centesimi) for p in smash.prezzi] == [
        ("Panino single hamb.", 700), ("Panino double hamb.", 850),
        ("Menù single hamb.", 1000), ("Menù double hamb.", 1200),
    ]


def test_los_pollos_solo_prezzi_single(connessione):
    voce = MenuRepository(connessione).leggi_voce(LOS_POLLOS_CLASSIC)
    assert [(p.etichetta_formato, p.prezzo_centesimi) for p in voce.prezzi] == [
        ("Panino single hamb.", 700), ("Menù single hamb.", 1100),
    ]


def test_prezzo_unico_senza_formato(connessione):
    voce = MenuRepository(connessione).leggi_voce(PATATINE_STICK)
    assert voce.ha_prezzo_unico() is True
    assert voce.prezzi[0].etichetta_formato is None


def test_voce_inesistente(connessione):
    assert MenuRepository(connessione).leggi_voce(99999) is None


def test_categoria_inesistente(connessione):
    assert MenuRepository(connessione).leggi_categoria(99) is None


def test_voce_nascosta_esclusa_solo_dal_menu_attivo(connessione):
    repo = MenuRepository(connessione)
    repo.imposta_attiva(SMASH_BURGER, False)
    attive = repo.leggi_menu()[2].voci
    tutte = repo.leggi_menu(solo_attive=False)[2].voci
    assert SMASH_BURGER not in {v.id for v in attive}
    nascosta = next(v for v in tutte if v.id == SMASH_BURGER)
    assert nascosta.attiva is False
    assert len(nascosta.prezzi) == 4  # i prezzi restano


def test_categoria_senza_voci_attive_resta_nel_repository(connessione):
    repo = MenuRepository(connessione)
    for voce in repo.leggi_menu()[3].voci:  # Kids Menù
        repo.imposta_attiva(voce.id, False)
    kids = next(c for c in repo.leggi_menu() if c.id == KIDS_MENU)
    assert kids.voci == []  # nasconderla dal menù pubblico è compito di MenuService


# --- Menù: nome unico ---

def test_esiste_nome_senza_maiuscole_e_accenti(connessione):
    repo = MenuRepository(connessione)
    assert repo.esiste_nome(BURGER, "Smash Burger") is True
    assert repo.esiste_nome(BURGER, "smash burger") is True
    assert repo.esiste_nome(BURGER, "Nuovo Burger") is False
    assert repo.esiste_nome(SOFT_DRINKS, "Smash Burger") is False  # altra categoria


def test_esiste_nome_esclude_la_voce_in_modifica(connessione):
    assert MenuRepository(connessione).esiste_nome(BURGER, "Smash Burger", escludi_voce_id=SMASH_BURGER) is False


# --- Menù: scrittura ---

def test_inserisci_voce_con_prezzi_e_rileggi(connessione):
    repo = MenuRepository(connessione)
    voce_id = repo.inserisci_voce(VoceMenu(BURGER, "Burger di prova", 8, descrizione="Solo per i test"))
    repo.sostituisci_prezzi(voce_id, [
        PrezzoVoce(750, formato_id=PANINO_SINGLE), PrezzoVoce(1050, formato_id=MENU_SINGLE),
    ])
    voce = repo.leggi_voce(voce_id)
    assert (voce.nome, voce.descrizione, voce.attiva) == ("Burger di prova", "Solo per i test", True)
    assert [(p.etichetta_formato, p.prezzo_centesimi) for p in voce.prezzi] == [
        ("Panino single hamb.", 750), ("Menù single hamb.", 1050),
    ]


def test_sostituisci_prezzi_toglie_quelli_vecchi(connessione):
    repo = MenuRepository(connessione)
    repo.sostituisci_prezzi(SMASH_BURGER, [PrezzoVoce(720, formato_id=PANINO_SINGLE)])
    assert [(p.formato_id, p.prezzo_centesimi) for p in repo.leggi_voce(SMASH_BURGER).prezzi] == [
        (PANINO_SINGLE, 720),
    ]


def test_aggiorna_voce(connessione):
    repo = MenuRepository(connessione)
    voce = repo.leggi_voce(SMASH_BURGER)
    voce.descrizione = "Hamburger, insalata, salsa smash"
    voce.posizione = 9
    repo.aggiorna_voce(voce)
    riletta = repo.leggi_voce(SMASH_BURGER)
    assert (riletta.descrizione, riletta.posizione) == ("Hamburger, insalata, salsa smash", 9)
    assert len(riletta.prezzi) == 4  # i prezzi non cambiano


def test_testo_con_apici_salvato_come_testo(connessione):
    repo = MenuRepository(connessione)
    nome = "Bro's '; DROP TABLE voci_menu; --"
    voce_id = repo.inserisci_voce(VoceMenu(BURGER, nome, 8))
    assert repo.leggi_voce(voce_id).nome == nome
    assert len(repo.leggi_menu(solo_attive=False)[2].voci) == 8  # la tabella esiste ancora


# --- Utenti ---

def test_utente_inserito_e_riletto(connessione):
    repo = UtenteRepository(connessione)
    utente_id = repo.inserisci(Utente("prova.repository@example.com", "$argon2id$finto"))
    letto = repo.leggi_per_email("Prova.Repository@example.com")
    assert letto.id == utente_id
    assert letto.attivo is True
    assert letto.creato_il is not None
    assert repo.leggi_per_id(utente_id).email == "prova.repository@example.com"


def test_utente_inesistente(connessione):
    repo = UtenteRepository(connessione)
    assert repo.leggi_per_email("nessuno@example.com") is None
    assert repo.leggi_per_id(99999) is None


def test_aggiorna_password_hash(connessione):
    repo = UtenteRepository(connessione)
    utente_id = repo.inserisci(Utente("prova.hash@example.com", "$argon2id$vecchio"))
    repo.aggiorna_password_hash(utente_id, "$argon2id$nuovo")
    assert repo.leggi_per_id(utente_id).password_hash == "$argon2id$nuovo"
