from datetime import datetime, timedelta

from app.modelli.orari import StatoApertura
from app.servizi.orari import NOMI_GIORNI


def euro(centesimi: int) -> str:
    """
    Filtro Jinja: prezzo in centesimi nel formato italiano. 750 -> "7,50 €".
    """
    return f"{centesimi // 100},{centesimi % 100:02d} €"


def prezzo_per_modulo(centesimi: int) -> str:
    """
    Prezzo come lo scrive il proprietario nel modulo, senza simbolo dell'euro. 750 -> "7,50".
    """
    return f"{centesimi // 100},{centesimi % 100:02d}"


def telefono_leggibile(telefono: str) -> str:
    """
    Filtro Jinja: numero salvato senza spazi, mostrato a gruppi. "+390810000000" -> "+39 081 000 0000".
    Regola provvisoria per i numeri italiani di 10 cifre; gli altri si mostrano come sono salvati.
    """
    cifre = telefono[3:]
    if telefono.startswith("+39") and cifre.isdigit() and len(cifre) == 10:
        return f"+39 {cifre[:3]} {cifre[3:6]} {cifre[6:]}"
    return telefono


def ora(valore) -> str:
    """
    Filtro Jinja: ora nel formato 18:00.
    """
    return valore.strftime("%H:%M")


def descrivi_stato_apertura(stato: StatoApertura, adesso: datetime) -> str:
    """
    Stato di apertura scritto per esteso, non solo con un colore:
    "Aperto · chiude alle 01:00", "Chiuso · apre oggi alle 18:00", "Chiuso · apre mercoledì alle 12:00".
    """
    if stato.aperto:
        return f"Aperto · chiude alle {ora(stato.turno_in_corso.ora_fine)}"
    if stato.prossima_apertura is None:
        return "Chiuso · orari non disponibili"
    oggi = adesso.replace(tzinfo=None).date()
    giorno = stato.prossima_apertura.date()
    if giorno == oggi:
        quando = "oggi"
    elif giorno == oggi + timedelta(days=1):
        quando = "domani"
    else:
        quando = NOMI_GIORNI[giorno.isoweekday()]
    return f"Chiuso · apre {quando} alle {ora(stato.prossima_apertura)}"
