import re
from datetime import date, datetime, time, timedelta

from app.eccezioni import DatiNonValidiError
from app.modelli.orari import StatoApertura, Turno
from app.repository.orari import OrariRepository

NOMI_GIORNI = {
    1: "lunedì", 2: "martedì", 3: "mercoledì", 4: "giovedì", 5: "venerdì", 6: "sabato", 7: "domenica",
}
_FORMATO_ORA = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")
# Un lunedì qualsiasi: serve solo a mettere i turni su una linea del tempo per il controllo
# delle sovrapposizioni.
_LUNEDI_DI_RIFERIMENTO = date(2026, 1, 5)


def ora_locale(adesso: datetime) -> datetime:
    """
    Porta l'istante nell'ora dell'orologio del locale, senza fuso, per confrontarlo con i turni.
    Args: adesso, già nel fuso del locale (lo prepara la rotta) oppure senza fuso.
    """
    return adesso.replace(tzinfo=None)


def calcola_stato(turni: list[Turno], adesso: datetime) -> StatoApertura:
    """
    Il locale è aperto se l'istante cade in un turno di oggi oppure in un turno di ieri che supera
    la mezzanotte (nessun turno dura più di 24 ore). Inizio incluso, fine esclusa.
    Returns: StatoApertura con il turno in corso, oppure con la prossima apertura.
    """
    locale = ora_locale(adesso)
    oggi = locale.date()
    for giorno in (oggi - timedelta(days=1), oggi):
        for turno in turni:
            if turno.giorno_settimana != giorno.isoweekday():
                continue
            inizio, fine = turno.intervallo(giorno)
            if inizio <= locale < fine:
                return StatoApertura(aperto=True, turno_in_corso=turno)
    return StatoApertura(aperto=False, prossima_apertura=prossima_apertura(turni, locale))


def prossima_apertura(turni: list[Turno], locale: datetime) -> datetime | None:
    """
    Primo inizio di turno dopo l'istante, cercato da oggi agli 8 giorni successivi
    (con un solo turno a settimana, appena finito, la riapertura è 7 giorni dopo).
    Returns: data e ora locali, oppure None se il calendario non ha turni.
    """
    for scostamento in range(8):
        giorno = locale.date() + timedelta(days=scostamento)
        inizi = sorted(
            datetime.combine(giorno, turno.ora_inizio)
            for turno in turni if turno.giorno_settimana == giorno.isoweekday()
        )
        for inizio in inizi:
            if inizio > locale:
                return inizio
    return None


def converti_ora(testo: str) -> time | None:
    """
    Returns: l'ora scritta nel formato HH:MM (da 00:00 a 23:59), oppure None se il formato è sbagliato.
    """
    corrispondenza = _FORMATO_ORA.match(testo.strip()) if isinstance(testo, str) else None
    if corrispondenza is None:
        return None
    return time(int(corrispondenza.group(1)), int(corrispondenza.group(2)))


def valida_turni(righe: list[tuple]) -> list[Turno]:
    """
    Controlla il calendario inviato dal proprietario: giorno da 1 a 7, ore nel formato HH:MM,
    inizio diverso dalla fine, nessuna sovrapposizione (anche oltre la mezzanotte e tra domenica
    e lunedì). Raccoglie tutti gli errori invece di fermarsi al primo.
    Args: righe, tuple (giorno, ora_inizio, ora_fine); giorno numero o testo, ore come testo "HH:MM".
    Returns: i Turni pronti da salvare.
    Raises: DatiNonValidiError con l'elenco dei messaggi.
    """
    messaggi = []
    turni = []
    for numero, (giorno, inizio_testo, fine_testo) in enumerate(righe, start=1):
        try:
            giorno = int(giorno)
        except (TypeError, ValueError):
            giorno = None
        if giorno not in NOMI_GIORNI:
            messaggi.append(f"Turno {numero}: giorno non valido.")
            continue
        inizio, fine = converti_ora(inizio_testo), converti_ora(fine_testo)
        nome = NOMI_GIORNI[giorno].capitalize()
        if inizio is None or fine is None:
            messaggi.append(f"{nome}: scrivi le ore nel formato HH:MM, es. 18:30.")
            continue
        if inizio == fine:
            messaggi.append(f"{nome}: inizio e fine del turno non possono essere uguali.")
            continue
        turni.append(Turno(giorno, inizio, fine))

    if not messaggi:
        messaggi = _sovrapposizioni(turni)
    if messaggi:
        raise DatiNonValidiError(messaggi)
    return turni


def _sovrapposizioni(turni: list[Turno]) -> list[str]:
    """
    Mette i turni su una settimana di riferimento più una copia spostata di 7 giorni, così il lunedì
    che segue la domenica esiste sulla linea del tempo; ordina per inizio e controlla che nessun
    turno inizi prima della fine del precedente. Turni adiacenti (fine = inizio) sono ammessi.
    Returns: i messaggi di errore, senza ripetizioni; lista vuota se non ci sono sovrapposizioni.
    """
    intervalli = []
    for turno in turni:
        giorno = _LUNEDI_DI_RIFERIMENTO + timedelta(days=turno.giorno_settimana - 1)
        for settimana in (0, 7):
            inizio, fine = turno.intervallo(giorno + timedelta(days=settimana))
            intervalli.append((inizio, fine, turno))
    intervalli.sort(key=lambda intervallo: intervallo[0])

    messaggi = []
    precedente = None
    for intervallo in intervalli:
        if precedente is not None and intervallo[0] < precedente[1]:
            messaggio = f"Turni sovrapposti: {_descrivi(precedente[2])} e {_descrivi(intervallo[2])}."
            if messaggio not in messaggi:
                messaggi.append(messaggio)
        if precedente is None or intervallo[1] > precedente[1]:
            precedente = intervallo
    return messaggi


def _descrivi(turno: Turno) -> str:
    """
    Returns: il turno scritto per esteso, es. "domenica 18:00-02:00".
    """
    return (f"{NOMI_GIORNI[turno.giorno_settimana]} "
            f"{turno.ora_inizio.strftime('%H:%M')}-{turno.ora_fine.strftime('%H:%M')}")


class OrariService:
    """
    Calendario settimanale e stato "aperto ora". Le regole sono nelle funzioni di questo modulo,
    che non usano il database e si testano da sole; il servizio le collega al repository.
    """

    def __init__(self, connessione):
        self._conn = connessione
        self._repo = OrariRepository(connessione)

    def leggi_turni(self) -> list[Turno]:
        """
        Returns: i turni della settimana, in ordine di giorno e di ora di inizio.
        """
        return self._repo.leggi_turni()

    def stato_apertura(self, adesso: datetime) -> StatoApertura:
        """
        Args: adesso, l'istante da controllare nel fuso del locale (la rotta passa l'ora attuale,
        i test un istante scelto da loro).
        Returns: lo StatoApertura del locale in quell'istante.
        """
        return calcola_stato(self._repo.leggi_turni(), adesso)

    def salva_turni(self, righe: list[tuple]) -> None:
        """
        Valida e salva l'intero calendario in una transazione: o tutti i turni nuovi, o nessuna modifica.
        Raises: DatiNonValidiError se una regola è violata (il database non viene toccato).
        """
        turni = valida_turni(righe)
        try:
            self._repo.sostituisci_turni(turni)
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
