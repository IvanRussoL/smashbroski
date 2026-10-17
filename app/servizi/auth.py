from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.eccezioni import DatiNonValidiError
from app.modelli.utente import Utente
from app.repository.utente import UtenteRepository

LUNGHEZZA_MINIMA_PASSWORD = 12
LUNGHEZZA_MASSIMA_EMAIL = 255

# Argon2id con i parametri predefiniti della libreria (argon2-cffi).
_HASHER = PasswordHasher()
# Hash di una password che nessuno usa: il login lo verifica quando l'email non esiste, così il
# tempo di risposta è lo stesso e non rivela quali email sono registrate.
_HASH_FITTIZIO = _HASHER.hash("password-fittizia-per-email-inesistenti")


class AuthService:
    """
    Login del proprietario e creazione del suo account. Le password non vengono mai salvate né
    restituite in chiaro: solo l'hash Argon2id.
    """

    def __init__(self, connessione, hasher: PasswordHasher | None = None):
        self._conn = connessione
        self._utenti = UtenteRepository(connessione)
        self._hasher = hasher or _HASHER
        self._hash_fittizio = _HASH_FITTIZIO if hasher is None else self._hasher.hash("password-fittizia")

    def login(self, email: str, password: str) -> Utente | None:
        """
        Controlla email e password. La verifica Argon2 si esegue sempre, anche per un'email
        inesistente (contro l'hash fittizio). Se i parametri di Argon2 sono cambiati, ricalcola
        e salva l'hash.
        Returns: l'Utente se le credenziali sono corrette e l'account è attivo; altrimenti None,
        senza dire quale controllo è fallito.
        """
        utente = self._utenti.leggi_per_email((email or "").strip())
        corretta = self._verifica(utente.password_hash if utente else self._hash_fittizio, password or "")
        if utente is None or not corretta or not utente.attivo:
            return None
        if self._hasher.check_needs_rehash(utente.password_hash):
            utente.password_hash = self._hasher.hash(password)
            self._utenti.aggiorna_password_hash(utente.id, utente.password_hash)
            self._conn.commit()
        return utente

    def crea_proprietario(self, email: str, password: str) -> int:
        """
        Crea l'account del proprietario (usato dal comando flask crea-proprietario).
        Returns: l'id del nuovo utente.
        Raises: DatiNonValidiError se l'email non è valida o è già registrata, o se la password
        ha meno di 12 caratteri.
        """
        email = (email or "").strip().lower()
        messaggi = []
        if not email or "@" not in email or len(email) > LUNGHEZZA_MASSIMA_EMAIL:
            messaggi.append("L'email non è valida.")
        elif self._utenti.leggi_per_email(email) is not None:
            messaggi.append("Esiste già un account con questa email.")
        if len(password or "") < LUNGHEZZA_MINIMA_PASSWORD:
            messaggi.append(f"La password deve avere almeno {LUNGHEZZA_MINIMA_PASSWORD} caratteri.")
        if messaggi:
            raise DatiNonValidiError(messaggi)

        utente_id = self._utenti.inserisci(Utente(email=email, password_hash=self._hasher.hash(password)))
        self._conn.commit()
        return utente_id

    def _verifica(self, password_hash: str, password: str) -> bool:
        """
        Returns: True se la password corrisponde all'hash; False se non corrisponde o l'hash non è valido.
        """
        try:
            return self._hasher.verify(password_hash, password)
        except (VerificationError, InvalidHashError):
            return False
