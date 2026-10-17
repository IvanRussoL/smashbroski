from datetime import time, timedelta

from app.modelli.orari import Turno


def _a_time(valore) -> time:
    """
    Il driver restituisce le colonne TIME come timedelta (durata dalla mezzanotte): le riporta a time.
    """
    if isinstance(valore, timedelta):
        secondi = int(valore.total_seconds())
        return time(secondi // 3600, secondi % 3600 // 60, secondi % 60)
    return valore


class OrariRepository:
    """
    Accesso alla tabella orari_settimanali. Non fa commit e non controlla le sovrapposizioni:
    lo fa OrariService.
    """

    def __init__(self, connessione):
        self._conn = connessione

    def leggi_turni(self) -> list[Turno]:
        """
        Returns: tutti i turni della settimana, in ordine di giorno e di ora di inizio.
        """
        with self._conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT id, giorno_settimana, ora_inizio, ora_fine FROM orari_settimanali "
                "ORDER BY giorno_settimana, ora_inizio"
            )
            righe = cur.fetchall()
        return [
            Turno(r["giorno_settimana"], _a_time(r["ora_inizio"]), _a_time(r["ora_fine"]), id=r["id"])
            for r in righe
        ]

    def sostituisci_turni(self, turni: list[Turno]) -> None:
        """
        Sostituisce l'intero calendario: cancella tutti i turni e inserisce quelli nuovi.
        Il servizio lo chiama dopo aver validato i turni, nella stessa transazione.
        """
        with self._conn.cursor() as cur:
            cur.execute("DELETE FROM orari_settimanali")
            for turno in turni:
                cur.execute(
                    "INSERT INTO orari_settimanali (giorno_settimana, ora_inizio, ora_fine) VALUES (%s, %s, %s)",
                    (turno.giorno_settimana, turno.ora_inizio, turno.ora_fine),
                )
