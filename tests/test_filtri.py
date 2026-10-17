from datetime import datetime, time

import pytest

from app.formato import euro, telefono_leggibile, descrivi_stato_apertura
from app.modelli.orari import StatoApertura, Turno


@pytest.mark.parametrize("centesimi, testo", [
    (700, "7,00 €"), (750, "7,50 €"), (1, "0,01 €"), (99999, "999,99 €"), (1050, "10,50 €"),
])
def test_euro(centesimi, testo):
    assert euro(centesimi) == testo


def test_telefono_leggibile():
    assert telefono_leggibile("+390810000000") == "+39 081 000 0000"
    assert telefono_leggibile("+3908100000") == "+3908100000"  # non 10 cifre: come salvato


ADESSO = datetime(2026, 10, 20, 10, 0)  # martedì


def test_testo_aperto():
    stato = StatoApertura(True, turno_in_corso=Turno(1, time(18, 0), time(1, 0)))
    assert descrivi_stato_apertura(stato, ADESSO) == "Aperto · chiude alle 01:00"


@pytest.mark.parametrize("prossima, testo", [
    (datetime(2026, 10, 20, 18, 0), "Chiuso · apre oggi alle 18:00"),
    (datetime(2026, 10, 21, 12, 0), "Chiuso · apre domani alle 12:00"),
    (datetime(2026, 10, 23, 12, 0), "Chiuso · apre venerdì alle 12:00"),
])
def test_testo_chiuso(prossima, testo):
    assert descrivi_stato_apertura(StatoApertura(False, prossima_apertura=prossima), ADESSO) == testo


def test_testo_orari_non_disponibili():
    assert descrivi_stato_apertura(StatoApertura(False), ADESSO) == "Chiuso · orari non disponibili"
