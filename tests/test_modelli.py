from datetime import date, datetime, time

from app.modelli.impostazioni import Impostazioni
from app.modelli.menu import PrezzoVoce, VoceMenu
from app.modelli.orari import Turno


def test_turno_supera_mezzanotte():
    assert Turno(1, time(18, 0), time(1, 0)).supera_mezzanotte() is True
    assert Turno(1, time(12, 0), time(15, 0)).supera_mezzanotte() is False


def test_turno_intervallo_finisce_giorno_dopo():
    # Lunedì 19 ottobre 2026, turno 18:00-01:00
    inizio, fine = Turno(1, time(18, 0), time(1, 0)).intervallo(date(2026, 10, 19))
    assert inizio == datetime(2026, 10, 19, 18, 0)
    assert fine == datetime(2026, 10, 20, 1, 0)


def test_turno_intervallo_stesso_giorno():
    inizio, fine = Turno(1, time(12, 0), time(15, 0)).intervallo(date(2026, 10, 19))
    assert inizio == datetime(2026, 10, 19, 12, 0)
    assert fine == datetime(2026, 10, 19, 15, 0)


def test_ha_prezzo_unico():
    bevanda = VoceMenu(5, "Acqua 50cl", 1, prezzi=[PrezzoVoce(100)])
    panino = VoceMenu(3, "Smash Burger", 1, prezzi=[PrezzoVoce(700, formato_id=5), PrezzoVoce(1000, formato_id=7)])
    assert bevanda.ha_prezzo_unico() is True
    assert panino.ha_prezzo_unico() is False


def test_link_maps():
    impostazioni = Impostazioni(
        "SmashBroski Pompei", "Vico dei Paninari, 7 - 80045 Pompei (NA)", "+390810000000",
        "info@example.com", "https://example.com/facebook-segnaposto", "https://example.com/instagram-segnaposto",
    )
    link = impostazioni.link_maps()
    assert link == (
        "https://www.google.com/maps/search/?api=1&query="
        "Vico+dei+Paninari%2C+7+-+80045+Pompei+%28NA%29"
    )
    assert "maps.app.goo.gl" not in link
