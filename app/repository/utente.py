from app.modelli.utente import Utente

_SELECT = (
    "SELECT id, email, password_hash, attivo, creato_il, totp_segreto, totp_attivo, totp_ultimo_passo FROM utenti "
)


def _da_riga(riga: dict) -> Utente:
    """
    Trasforma una riga di utenti in un Utente, convertendo attivo e totp_attivo da 0/1 a bool.
    """
    riga["attivo"] = bool(riga["attivo"])
    riga["totp_attivo"] = bool(riga["totp_attivo"])
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

    def aggiorna_attivo(self, utente_id: int, attivo: bool) -> None:
        """
        Attiva o disattiva un account: un account disattivato non entra e perde subito l'accesso.
        """
        with self._conn.cursor() as cur:
            cur.execute("UPDATE utenti SET attivo = %s WHERE id = %s", (attivo, utente_id))

    def salva_totp(self, utente_id: int, segreto_cifrato: str | None, attivo: bool) -> None:
        """
        Salva il segreto TOTP (già cifrato) e se la verifica in due passaggi è attiva; azzera
        l'ultimo intervallo usato. Con segreto None e attivo False la verifica è tolta.
        """
        with self._conn.cursor() as cur:
            cur.execute(
                "UPDATE utenti SET totp_segreto = %s, totp_attivo = %s, totp_ultimo_passo = NULL WHERE id = %s",
                (segreto_cifrato, attivo, utente_id),
            )

    def aggiorna_ultimo_passo(self, utente_id: int, passo: int) -> None:
        """
        Ricorda l'intervallo di 30 secondi dell'ultimo codice accettato: i codici dello stesso
        intervallo o di quelli prima non valgono più.
        """
        with self._conn.cursor() as cur:
            cur.execute("UPDATE utenti SET totp_ultimo_passo = %s WHERE id = %s", (passo, utente_id))

