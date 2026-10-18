from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template, url_for

from app.db import ottieni_connessione
from app.repository.impostazioni import ImpostazioniRepository
from app.servizi.menu import MenuService
from app.servizi.orari import NOMI_GIORNI, OrariService

bp = Blueprint("pubblico", __name__)


def ora_attuale(fuso_orario: str) -> datetime:
    """
    Istante attuale nel fuso del locale. Funzione separata così i test la sostituiscono.
    """
    return datetime.now(ZoneInfo(fuso_orario))


def _impostazioni():
    return ImpostazioniRepository(ottieni_connessione()).leggi()


def _orari_per_giorno(turni) -> list[dict]:
    """
    Returns: i 7 giorni da lunedì, ognuno con numero, nome e turni (lista vuota = chiuso).
    """
    return [
        {"numero": numero, "nome": nome.capitalize(),
         "turni": [turno for turno in turni if turno.giorno_settimana == numero]}
        for numero, nome in NOMI_GIORNI.items()
    ]


def _json_ld(impostazioni, turni) -> dict:
    """
    Dati strutturati schema.org Restaurant (RNF-10, AU-SEO04). Il telefono di prova non si inserisce.
    """
    giorni_inglesi = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday",
                      5: "Friday", 6: "Saturday", 7: "Sunday"}
    dati = {
        "@context": "https://schema.org",
        "@type": "Restaurant",
        "name": impostazioni.nome_locale,
        "servesCuisine": "Hamburger",
        "address": impostazioni.indirizzo,
        "url": url_for("pubblico.home", _external=True),
        "hasMenu": url_for("pubblico.menu", _external=True),
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": giorni_inglesi[turno.giorno_settimana],
             "opens": turno.ora_inizio.strftime("%H:%M"), "closes": turno.ora_fine.strftime("%H:%M")}
            for turno in turni
        ],
    }
    if not impostazioni.telefono_di_prova:
        dati["telephone"] = impostazioni.telefono
    return dati


@bp.get("/")
def home():
    impostazioni = _impostazioni()
    servizio = OrariService(ottieni_connessione())
    adesso = ora_attuale(impostazioni.fuso_orario)
    turni = servizio.leggi_turni()
    return render_template(
        "home.html",
        impostazioni=impostazioni,
        stato=servizio.stato_apertura(adesso),
        adesso=adesso,
        oggi=adesso.isoweekday(),
        orari=_orari_per_giorno(turni),
        json_ld=_json_ld(impostazioni, turni),
    )


@bp.get("/menu")
def menu():
    return render_template(
        "menu.html",
        impostazioni=_impostazioni(),
        categorie=MenuService(ottieni_connessione()).menu_pubblico(),
    )


@bp.get("/info")
def info():
    """
    Orari della settimana e contatti, con il giorno di oggi evidenziato.
    """
    impostazioni = _impostazioni()
    servizio = OrariService(ottieni_connessione())
    adesso = ora_attuale(impostazioni.fuso_orario)
    return render_template(
        "info.html",
        impostazioni=impostazioni,
        stato=servizio.stato_apertura(adesso),
        adesso=adesso,
        oggi=adesso.isoweekday(),
        orari=_orari_per_giorno(servizio.leggi_turni()),
    )


@bp.get("/privacy")
def privacy():
    return render_template("privacy.html", impostazioni=_impostazioni())
