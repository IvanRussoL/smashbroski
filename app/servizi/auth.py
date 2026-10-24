from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.eccezioni import DatiNonValidiError, NonTrovatoError
from app.modelli.utente import Utente
from app.repository.utente import UtenteRepository

LUNGHEZZA_MINIMA_PASSWORD = 12
# Oltre questa lunghezza la password è rifiutata: Argon2 su testi enormi farebbe lavorare il server a vuoto.
LUNGHEZZA_MASSIMA_PASSWORD = 128
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
        password = password or ""
        troppo_lunga = len(password) > LUNGHEZZA_MASSIMA_PASSWORD
        corretta = self._verifica(utente.password_hash if utente else self._hash_fittizio,
                                  "" if troppo_lunga else password) and not troppo_lunga
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
        elif len(password) > LUNGHEZZA_MASSIMA_PASSWORD:
            messaggi.append(f"La password può avere al massimo {LUNGHEZZA_MASSIMA_PASSWORD} caratteri.")
        if messaggi:
            raise DatiNonValidiError(messaggi)

        utente_id = self._utenti.inserisci(Utente(email=email, password_hash=self._hasher.hash(password)))
        self._conn.commit()
        return utente_id

    def cambia_password(self, utente_id: int, attuale: str, nuova: str, conferma: str) -> None:
        """
        Cambio della password dall'area proprietario: serve la password attuale, così chi trova
        il telefono con la sessione aperta non può cambiarla. Raccoglie tutti gli errori.
        Raises: DatiNonValidiError se la password attuale è sbagliata, la nuova ha meno di 12
        caratteri, è uguale all'attuale o non coincide con la conferma; NonTrovatoError se
        l'utente non esiste.
        """
        utente = self._utenti.leggi_per_id(utente_id)
        if utente is None:
            raise NonTrovatoError("Utente non trovato.")
        messaggi = []
        if not self._verifica(utente.password_hash, attuale or ""):
            messaggi.append("La password attuale non è corretta.")
        messaggi += self._controlla_nuova_password(nuova, conferma)
        if not messaggi and nuova == attuale:
            messaggi.append("La nuova password deve essere diversa da quella attuale.")
        if messaggi:
            raise DatiNonValidiError(messaggi)
        self._utenti.aggiorna_password_hash(utente.id, self._hasher.hash(nuova))
        self._conn.commit()

    def reimposta_password(self, email: str, nuova: str) -> None:
        """
        Nuova password scelta dallo sviluppatore (comando flask reimposta-password), per quando il
        proprietario l'ha dimenticata: non serve quella attuale.
        Raises: DatiNonValidiError se l'email non è registrata o la password ha meno di 12 caratteri.
        """
        utente = self._utente_da_email(email)
        messaggi = self._controlla_nuova_password(nuova, nuova)
        if messaggi:
            raise DatiNonValidiError(messaggi)
        self._utenti.aggiorna_password_hash(utente.id, self._hasher.hash(nuova))
        self._conn.commit()

    def imposta_attivo(self, email: str, attivo: bool) -> None:
        """
        Disattiva o riattiva un account (comandi flask disattiva-proprietario e riattiva-proprietario).
        Raises: DatiNonValidiError se l'email non è registrata.
        """
        utente = self._utente_da_email(email)
        self._utenti.aggiorna_attivo(utente.id, attivo)
        self._conn.commit()

    def _utente_da_email(self, email: str) -> Utente:
        utente = self._utenti.leggi_per_email((email or "").strip())
        if utente is None:
            raise DatiNonValidiError(["Nessun account con questa email."])
        return utente

    @staticmethod
    def _controlla_nuova_password(nuova: str, conferma: str) -> list[str]:
        """
        Returns: i messaggi di errore sulla nuova password (lunghezza minima e massima, conferma); lista vuota se va bene.
        """
        messaggi = []
        if len(nuova or "") < LUNGHEZZA_MINIMA_PASSWORD:
            messaggi.append(f"La nuova password deve avere almeno {LUNGHEZZA_MINIMA_PASSWORD} caratteri.")
        elif len(nuova) > LUNGHEZZA_MASSIMA_PASSWORD:
            messaggi.append(f"La nuova password può avere al massimo {LUNGHEZZA_MASSIMA_PASSWORD} caratteri.")
        if (nuova or "") != (conferma or ""):
            messaggi.append("La nuova password e la conferma non coincidono.")
        return messaggi

    def _verifica(self, password_hash: str, password: str) -> bool:
        """
        Returns: True se la password corrisponde all'hash; False se non corrisponde o l'hash non è valido.
        """
        try:
            return self._hasher.verify(password_hash, password)
        except (VerificationError, InvalidHashError):
            return False
