from app.modelli.utente import Utente

_SELECT = "SELECT id, email, password_hash, attivo, creato_il FROM utenti "


def _da_riga(riga: dict) -> Utente:
    """
    Trasforma una riga di utenti in un Utente, convertendo attivo da 0/1 a bool.
    """
    riga["attivo"] = bool(riga["attivo"])
    return Utente(**riga)


class UtenteRepository:
    """
    Accesso alla tabella utenti. Non fa commit: lo decide il servizio.
    """

    def __init__(self, connessione):
        self._conn = connessione

    def leggi_per_id(self, utente_id: int) -> Utente | None:
        """
        Returns: l'Utente con quell'id, oppure None se non esiste.
        """
        with self._conn.cursor(dictionary=True) as cur:
            cur.execute(_SELECT + "WHERE id = %s", (utente_id,))
            riga = cur.fetchone()
        return _da_riga(riga) if riga else None

    def leggi_per_email(self, email: str) -> Utente | None:
        """
        Cerca un utente dall'email, senza distinguere maiuscole e minuscole (confronto del database).
        Returns: l'Utente, oppure None se l'email non è registrata.
        """
        with self._conn.cursor(dictionary=True) as cur:
            cur.execute(_SELECT + "WHERE email = %s", (email,))
            riga = cur.fetchone()
        return _da_riga(riga) if riga else None

    def inserisci(self, utente: Utente) -> int:
        """
        Inserisce un nuovo utente; creato_il lo scrive MySQL.
        Returns: l'id assegnato da MySQL.
        Raises: mysql.connector.IntegrityError se l'email è già registrata.
        """
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO utenti (email, password_hash, attivo) VALUES (%s, %s, %s)",
                (utente.email, utente.password_hash, utente.attivo),
            )
            return cur.lastrowid

    def aggiorna_password_hash(self, utente_id: int, password_hash: str) -> None:
        """
        Salva un nuovo hash della password (es. ricalcolato con parametri di Argon2 aggiornati).
        """
        with self._conn.cursor() as cur:
            cur.execute("UPDATE utenti SET password_hash = %s WHERE id = %s", (password_hash, utente_id))
