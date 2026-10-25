from datetime import datetime


class CodiciRiservaRepository:
    """
    Accesso alla tabella codici_riserva. Contiene solo hash; non fa commit: lo decide il servizio.
    """

    def __init__(self, connessione):
        self._conn = connessione

    def sostituisci(self, utente_id: int, hash_codici: list[str]) -> None:
        """
        Cancella i codici di riserva dell'utente, anche quelli non usati, e salva i nuovi.
        """
        with self._conn.cursor() as cur:
            cur.execute("DELETE FROM codici_riserva WHERE utente_id = %s", (utente_id,))
            for codice_hash in hash_codici:
                cur.execute(
                    "INSERT INTO codici_riserva (utente_id, codice_hash) VALUES (%s, %s)", (utente_id, codice_hash)
                )

    def leggi_non_usati(self, utente_id: int) -> list[tuple[int, str]]:
        """
        Returns: id e hash dei codici di riserva dell'utente non ancora usati.
        """
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT id, codice_hash FROM codici_riserva WHERE utente_id = %s AND usato_il IS NULL ORDER BY id",
                (utente_id,),
            )
            return [(riga[0], riga[1]) for riga in cur.fetchall()]

    def segna_usato(self, codice_id: int, usato_il: datetime) -> None:
        """
        Segna un codice come usato: non vale più.
        """
        with self._conn.cursor() as cur:
            cur.execute("UPDATE codici_riserva SET usato_il = %s WHERE id = %s", (usato_il, codice_id))

    def cancella(self, utente_id: int) -> None:
        """
        Cancella tutti i codici di riserva dell'utente (verifica in due passaggi tolta).
        """
        with self._conn.cursor() as cur:
            cur.execute("DELETE FROM codici_riserva WHERE utente_id = %s", (utente_id,))
