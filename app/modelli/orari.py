from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


@dataclass
class Turno:
    """
    Turno di apertura nel giorno in cui inizia (1 = lunedì ... 7 = domenica, come isoweekday()),
    con gli orari nell'ora locale del locale. Se ora_fine è prima di ora_inizio,
    il turno finisce il giorno dopo.
    """
    giorno_settimana: int
    ora_inizio: time
    ora_fine: time
    id: int | None = None

    def supera_mezzanotte(self) -> bool:
        """
        Returns: True se il turno finisce il giorno dopo (es. 18:00-01:00).
        """
        return self.ora_fine < self.ora_inizio

    def intervallo(self, giorno: date) -> tuple[datetime, datetime]:
        """
        Inizio e fine del turno come data e ora complete, se il turno inizia nel giorno indicato.
        Sono in ora locale senza fuso: il confronto con l'istante attuale, convertito nello
        stesso fuso, lo fa OrariService.
        Returns: (inizio, fine); con un turno oltre la mezzanotte la fine è nel giorno dopo.
        """
        inizio = datetime.combine(giorno, self.ora_inizio)
        giorno_fine = giorno + timedelta(days=1) if self.supera_mezzanotte() else giorno
        fine = datetime.combine(giorno_fine, self.ora_fine)
        return inizio, fine


@dataclass
class StatoApertura:
    """
    Risultato del calcolo "aperto ora", fatto da OrariService; la home lo mostra soltanto.
    Aperto: turno_in_corso indica quando chiude. Chiuso: prossima_apertura indica quando riapre,
    oppure è None se il calendario non ha turni ("orari non disponibili").
    """
    aperto: bool
    turno_in_corso: Turno | None = None
    prossima_apertura: datetime | None = None  # ora locale, senza fuso
