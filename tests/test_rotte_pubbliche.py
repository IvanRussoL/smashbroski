import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from app.rotte import pubblico

ROMA = ZoneInfo("Europe/Rome")


def html(risposta) -> str:
    return risposta.get_data(as_text=True)


def json_ld(pagina: str) -> dict:
    blocco = re.search(r'<script type="application/ld\+json">(.*?)</script>', pagina, re.S)
    return json.loads(blocco.group(1))


@pytest.fixture
def ora_fissa(monkeypatch):
    """
    Sostituisce l'ora attuale della home con un istante scelto dal test.
    """
    def imposta(anno, mese, giorno, ore, minuti=0):
        istante = datetime(anno, mese, giorno, ore, minuti, tzinfo=ROMA)
        monkeypatch.setattr(pubblico, "ora_attuale", lambda fuso: istante)
    return imposta


# --- Home ---

def test_home_contenuti(client):
    risposta = client.get("/")
    pagina = html(risposta)
    assert risposta.status_code == 200
    assert pagina.count("<h1") == 1
    titolo = re.search(r"<title>(.*?)</title>", pagina).group(1)
    assert "Hamburgeria" in titolo and "Pompei" in titolo
    assert '<meta name="description"' in pagina
    assert "https://www.google.com/maps/search/?api=1&amp;query=Vico+dei+Paninari" in pagina
    assert "Vico dei Paninari, 7 - 80045 Pompei (NA)" in pagina
    assert 'href="/info"' in pagina
    assert 'href="/privacy"' in pagina
    assert "wa.me" not in pagina


def test_home_nessun_link_area_riservata(client):
    for indirizzo in ("/", "/menu", "/info", "/privacy"):
        pagina = html(client.get(indirizzo))
        assert "/auth" not in pagina
        assert "/proprietario" not in pagina


def test_home_stato_apertura_chiuso(client, ora_fissa):
    ora_fissa(2026, 10, 20, 10)  # martedì 10:00
    pagina = html(client.get("/"))
    assert "Chiuso · apre domani alle 12:00" in pagina


def test_home_stato_apertura_dopo_mezzanotte(client, ora_fissa):
    ora_fissa(2026, 10, 20, 0, 30)  # martedì 00:30, turno di lunedì
    assert "Aperto · chiude alle 01:00" in html(client.get("/"))


def test_home_stato_apertura_tra_piu_giorni(client, ora_fissa):
    ora_fissa(2026, 10, 19, 1, 30)  # lunedì 01:30, ancora il turno di domenica
    assert "Aperto · chiude alle 02:00" in html(client.get("/"))


def test_home_json_ld(client):
    dati = json_ld(html(client.get("/")))
    assert dati["@type"] == "Restaurant"
    assert dati["address"] == "Vico dei Paninari, 7 - 80045 Pompei (NA)"
    assert dati["hasMenu"].endswith("/menu")
    assert len(dati["openingHoursSpecification"]) == 10
    assert "telephone" not in dati  # telefono di prova


def test_home_json_ld_con_telefono_reale(client, database_modificato):
    with database_modificato.cursor() as cur:
        cur.execute("UPDATE impostazioni SET telefono_di_prova = FALSE")
    database_modificato.commit()
    assert json_ld(html(client.get("/")))["telephone"] == "+390810000000"
    assert "numero di prova" not in html(client.get("/info"))


def test_json_ld_escape(client, database_modificato):
    with database_modificato.cursor() as cur:
        cur.execute("UPDATE impostazioni SET nome_locale = %s", ("Smash</script><b>x",))
    database_modificato.commit()
    pagina = html(client.get("/"))
    assert "Smash</script>" not in pagina
    assert json_ld(pagina)["name"] == "Smash</script><b>x"


# --- Orari e contatti ---

def test_info_contenuti(client):
    risposta = client.get("/info")
    pagina = html(risposta)
    assert risposta.status_code == 200
    assert pagina.count("<h1") == 1
    assert "Orari e contatti" in re.search(r"<title>(.*?)</title>", pagina).group(1)
    assert 'href="tel:+390810000000"' in pagina
    assert "+39 081 000 0000" in pagina
    assert "numero di prova" in pagina
    assert 'href="mailto:info@example.com"' in pagina
    assert "https://www.google.com/maps/search/?api=1&amp;query=Vico+dei+Paninari" in pagina
    assert 'aria-current="page"' in pagina


def test_info_orari_martedi_chiuso(client):
    pagina = html(client.get("/info"))
    assert re.search(r"<dt>(?:<strong>)?Martedì(?: \(oggi\)</strong>)?</dt>\s*<dd>Chiuso</dd>", pagina)
    assert '<span class="turno">12:00–15:00</span> · <span class="turno">18:00–01:00</span>' in pagina


def test_info_oggi_evidenziato(client, ora_fissa):
    ora_fissa(2026, 10, 20, 10)  # martedì 10:00
    pagina = html(client.get("/info"))
    assert "<strong>Martedì (oggi)</strong>" in pagina
    assert "Chiuso · apre domani alle 12:00" in pagina
    assert pagina.count('class="orari-giorno oggi"') == 1


def test_info_azioni_rapide(client):
    pagina = html(client.get("/info"))
    azioni = re.search(r'<ul class="azioni-info">(.*?)</ul>', pagina, re.S).group(1)
    assert 'href="tel:+390810000000"' in azioni
    assert "https://www.google.com/maps/search/?api=1&amp;query=Vico+dei+Paninari" in azioni
    assert 'href="mailto:info@example.com"' in azioni
    for etichetta in ("Chiama", "Indicazioni", "Scrivi"):
        assert etichetta in azioni


def test_info_sezioni_e_ancore(client):
    pagina = html(client.get("/info"))
    for ancora in ('id="orari"', 'id="come-arrivare"', 'id="contatti"'):
        assert ancora in pagina
    assert "<iframe" not in pagina  # niente mappa incorporata: cookie di terze parti (RNF-11)


# --- Menù ---

def test_menu_struttura(client):
    risposta = client.get("/menu")
    pagina = html(risposta)
    assert risposta.status_code == 200
    assert pagina.count("<h1") == 1
    contenuto = pagina.split("<main")[1].split("</main>")[0]  # solo la pagina, senza navbar e footer
    assert re.findall(r'<h2 id="([a-z-]+)"', contenuto) == [
        "starters", "salad", "burger", "kids-menu", "soft-drinks", "beers", "the-originals",
    ]
    assert pagina.count("<h3>") == 25
    assert "Smash Cheeseburger" in pagina
    assert 'href="#kids-menu"' in pagina
    assert 'aria-current="page"' in pagina


def test_menu_indice_senza_torna_indice(client):
    pagina = html(client.get("/menu"))
    assert 'src="/static/js/indice.js"' in pagina  # evidenzia la categoria al tocco e durante lo scroll
    assert "Torna all'indice" not in pagina
    assert 'href="#indice"' not in pagina


def test_menu_prezzi_e_formati(client):
    pagina = html(client.get("/menu"))
    smash = pagina.split("Smash Burger</span>")[1].split("</article>")[0]
    assert "<dt>Panino single hamb.</dt>" in smash
    assert "<dd>7,00 €</dd>" in smash
    pollos = pagina.split("Los Pollos Classic</span>")[1].split("</article>")[0]
    assert "double" not in pollos
    acqua = pagina.split("Acqua 50cl</span>")[1].split("</article>")[0]
    assert '<p class="prezzo-unico">1,00 €</p>' in acqua


def test_menu_voce_nascosta_assente(client, database_modificato):
    with database_modificato.cursor() as cur:
        cur.execute("UPDATE voci_menu SET attiva = FALSE WHERE nome = 'Smash Burger'")
    database_modificato.commit()
    pagina = html(client.get("/menu"))
    assert "Smash Burger</span>" not in pagina
    assert pagina.count("<h3>") == 24


def test_menu_categoria_vuota_assente(client, database_modificato):
    with database_modificato.cursor() as cur:
        cur.execute("UPDATE voci_menu SET attiva = FALSE WHERE categoria_id = 4")  # Kids Menù
    database_modificato.commit()
    pagina = html(client.get("/menu"))
    assert 'id="kids-menu"' not in pagina
    assert 'href="#kids-menu"' not in pagina


def test_escape_testo_proprietario(client, database_modificato):
    with database_modificato.cursor() as cur:
        cur.execute("UPDATE voci_menu SET nome = '<b>Prova</b>' WHERE nome = 'Smash Burger'")
    database_modificato.commit()
    pagina = html(client.get("/menu"))
    assert "&lt;b&gt;Prova&lt;/b&gt;" in pagina
    assert "<b>Prova</b>" not in pagina


# --- Altre pagine ed errori ---

def test_privacy(client):
    risposta = client.get("/privacy")
    assert risposta.status_code == 200
    assert "Privacy e cookie" in html(risposta)


def test_nessun_generator(client):
    for indirizzo in ("/", "/menu", "/info", "/privacy"):
        assert 'name="generator"' not in html(client.get(indirizzo))


def test_pagine_pubbliche_senza_cookie(client):
    for indirizzo in ("/", "/menu", "/info", "/privacy"):
        assert "Set-Cookie" not in client.get(indirizzo).headers


def test_pagina_404(client):
    risposta = client.get("/pagina-inesistente")
    assert risposta.status_code == 404
    assert "Pagina non trovata." in html(risposta)
    assert 'href="/menu"' in html(risposta)  # pagina del sito, non quella di Flask


def test_nessuna_registrazione(client):
    assert client.get("/auth/register").status_code == 404
