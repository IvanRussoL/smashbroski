from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest

from app.eccezioni import DatiNonValidiError
from app.modelli.orari import Turno
from app.servizi.orari import OrariService, calcola_stato, valida_turni

ROMA = ZoneInfo("Europe/Rome")

# Orari iniziali (sezione 4 di PROGETTAZIONE.md), come li scrive il proprietario.
RIGHE_INIZIALI = [
    (1, "12:00", "15:00"), (1, "18:00", "01:00"),
    (3, "12:00", "15:00"), (3, "18:00", "01:00"),
    (4, "12:00", "15:00"), (4, "18:00", "01:00"),
    (5, "12:00", "15:00"), (5, "18:00", "01:00"),
    (6, "18:00", "02:00"),
    (7, "18:00", "02:00"),
]
CALENDARIO = valida_turni(RIGHE_INIZIALI)


def roma(giorno: int, ora: int, minuti: int = 0, fold: int = 0) -> datetime:
    """
    Istante di ottobre 2026 nel fuso di Roma: lunedì 19, martedì 20, mercoledì 21, sabato 24, domenica 25.
    """
    return datetime(2026, 10, giorno, ora, minuti, tzinfo=ROMA, fold=fold)


# --- 3.1 Stato di apertura ---

def test_lunedi_1200_aperto_inizio_incluso():
    stato = calcola_stato(CALENDARIO, roma(19, 12))
    assert stato.aperto is True
    assert stato.turno_in_corso.ora_fine == time(15, 0)


def test_lunedi_1459_aperto():
    assert calcola_stato(CALENDARIO, roma(19, 14, 59)).aperto is True


def test_lunedi_1500_chiuso_fine_esclusa():
    stato = calcola_stato(CALENDARIO, roma(19, 15))
    assert stato.aperto is False
    assert stato.prossima_apertura == datetime(2026, 10, 19, 18, 0)


def test_martedi_0030_aperto_per_turno_di_lunedi():
    stato = calcola_stato(CALENDARIO, roma(20, 0, 30))
    assert stato.aperto is True
    assert stato.turno_in_corso.giorno_settimana == 1
    assert stato.turno_in_corso.ora_fine == time(1, 0)


def test_martedi_0100_chiuso():
    stato = calcola_stato(CALENDARIO, roma(20, 1))
    assert stato.aperto is False
    assert stato.prossima_apertura == datetime(2026, 10, 21, 12, 0)


def test_martedi_1000_chiuso_apre_mercoledi():
    stato = calcola_stato(CALENDARIO, roma(20, 10))
    assert stato.aperto is False
    assert stato.prossima_apertura == datetime(2026, 10, 21, 12, 0)


def test_lunedi_0130_aperto_per_turno_di_domenica():
    stato = calcola_stato(CALENDARIO, roma(19, 1, 30))
    assert stato.aperto is True
    assert stato.turno_in_corso.giorno_settimana == 7


def test_sabato_1000_apre_stesso_giorno():
    stato = calcola_stato(CALENDARIO, roma(24, 10))
    assert stato.aperto is False
    assert stato.prossima_apertura == datetime(2026, 10, 24, 18, 0)


def test_domenica_0159_aperto_domenica_0200_chiuso():
    assert calcola_stato(CALENDARIO, roma(25, 1, 59)).aperto is True
    assert calcola_stato(CALENDARIO, roma(25, 2)).aperto is False


def test_cambio_ora_solare_ora_ripetuta():
    # Domenica 25/10/2026 alle 03:00 si torna alle 02:00: le 02:30 capitano due volte.
    for fold in (0, 1):
        stato = calcola_stato(CALENDARIO, roma(25, 2, 30, fold=fold))
        assert stato.aperto is False
        assert stato.prossima_apertura == datetime(2026, 10, 25, 18, 0)


def test_calendario_vuoto_nessuna_apertura():
    stato = calcola_stato([], roma(19, 12))
    assert stato.aperto is False
    assert stato.prossima_apertura is None


def test_un_solo_turno_prossima_apertura_dopo_7_giorni():
    stato = calcola_stato([Turno(1, time(12, 0), time(15, 0))], roma(19, 16))
    assert stato.prossima_apertura == datetime(2026, 10, 26, 12, 0)


# --- 3.2 Validazione del calendario ---

def test_calendario_iniziale_valido():
    assert len(CALENDARIO) == 10


def test_turni_stesso_giorno_sovrapposti_errore():
    with pytest.raises(DatiNonValidiError):
        valida_turni([(1, "12:00", "15:00"), (1, "14:00", "16:00")])


def test_turni_adiacenti_accettati():
    assert len(valida_turni([(1, "12:00", "15:00"), (1, "15:00", "18:00")])) == 2


def test_turno_oltre_mezzanotte_sovrapposto_giorno_dopo_errore():
    with pytest.raises(DatiNonValidiError) as errore:
        valida_turni([(7, "18:00", "02:00"), (1, "01:00", "03:00")])
    assert errore.value.messaggi == ["Turni sovrapposti: domenica 18:00-02:00 e lunedì 01:00-03:00."]


def test_turno_oltre_mezzanotte_adiacente_giorno_dopo_accettato():
    assert len(valida_turni([(7, "18:00", "02:00"), (1, "02:00", "04:00")])) == 2


def test_inizio_uguale_fine_errore():
    with pytest.raises(DatiNonValidiError):
        valida_turni([(1, "12:00", "12:00")])


@pytest.mark.parametrize("ora", ["25:00", "12.30", "", "24:00", "9:00"])
def test_ora_formato_non_valido_errore(ora):
    with pytest.raises(DatiNonValidiError):
        valida_turni([(1, ora, "15:00")])


@pytest.mark.parametrize("giorno", [0, 8, "x"])
def test_giorno_fuori_intervallo_errore(giorno):
    with pytest.raises(DatiNonValidiError):
        valida_turni([(giorno, "12:00", "15:00")])


def test_errori_raccolti_tutti_insieme():
    with pytest.raises(DatiNonValidiError) as errore:
        valida_turni([(0, "12:00", "15:00"), (1, "12:00", "12:00")])
    assert len(errore.value.messaggi) == 2


# --- Servizio con il database ---

def test_stato_apertura_dal_database(connessione):
    assert OrariService(connessione).stato_apertura(roma(20, 0, 30)).aperto is True


def test_salva_turni_validi(connessione):
    servizio = OrariService(connessione)
    servizio.salva_turni(RIGHE_INIZIALI)
    assert len(servizio.leggi_turni()) == 10


def test_salvataggio_rifiutato_non_modifica_orari(connessione):
    servizio = OrariService(connessione)
    prima = servizio.leggi_turni()
    with pytest.raises(DatiNonValidiError):
        servizio.salva_turni([(1, "12:00", "15:00"), (1, "14:00", "16:00")])
    assert servizio.leggi_turni() == prima
