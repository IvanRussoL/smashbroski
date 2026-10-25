import re
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.eccezioni import DatiNonValidiError, NonTrovatoError
from app.modelli.utente import Utente
from app.repository.utente import UtenteRepository

# 15 caratteri: minimo del NIST (SP 800-63B rev. 4) quando la password è l'unico fattore di accesso.
LUNGHEZZA_MINIMA_PASSWORD = 15
# Oltre questa lunghezza la password è rifiutata: Argon2 su testi enormi farebbe lavorare il server a vuoto.
LUNGHEZZA_MASSIMA_PASSWORD = 128
LUNGHEZZA_MASSIMA_EMAIL = 255
# Meno di 5 caratteri diversi (es. "aaaaaaaaaaaaaaa", "121212121212121"): password ripetitiva.
CARATTERI_DIVERSI_MINIMI = 5
# Nome del sito: una password che lo contiene è tra le prime che un attaccante prova (NIST, parole del contesto).
PAROLE_DEL_SITO = ("smashbroski",)
# Nel cambio password solo questo errore conta come tentativo sbagliato (app/limiti.py).
MESSAGGIO_ATTUALE_ERRATA = "La password attuale non è corretta."


def _carica_password_comuni() -> frozenset[str]:
    """
    Returns: le password comuni di app/dati/password_comuni.txt (fonte nel file), in minuscolo.
    """
    percorso = Path(__file__).resolve().parent.parent / "dati" / "password_comuni.txt"
    righe = percorso.read_text(encoding="utf-8").splitlines()
    return frozenset(riga for riga in righe if riga and not riga.startswith("#"))


PASSWORD_COMUNI = _carica_password_comuni()

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
        è troppo corta, troppo lunga o facile da indovinare.
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
        else:
            messaggi += _controlla_password_debole(password, email)
        if messaggi:
            raise DatiNonValidiError(messaggi)

        utente_id = self._utenti.inserisci(Utente(email=email, password_hash=self._hasher.hash(password)))
        self._conn.commit()
        return utente_id

    def cambia_password(self, utente_id: int, attuale: str, nuova: str, conferma: str) -> None:
        """
        Cambio della password dall'area proprietario: serve la password attuale, così chi trova
        il telefono con la sessione aperta non può cambiarla. Raccoglie tutti gli errori.
        Raises: DatiNonValidiError se la password attuale è sbagliata, la nuova è troppo corta,
        troppo lunga o facile da indovinare, è uguale all'attuale o non coincide con la conferma;
        NonTrovatoError se l'utente non esiste.
        """
        utente = self._utenti.leggi_per_id(utente_id)
        if utente is None:
            raise NonTrovatoError("Utente non trovato.")
        messaggi = []
        if not self._verifica(utente.password_hash, attuale or ""):
            messaggi.append(MESSAGGIO_ATTUALE_ERRATA)
        messaggi += self._controlla_nuova_password(nuova, conferma, utente.email)
        if not messaggi and nuova == attuale:
            messaggi.append("La nuova password deve essere diversa da quella attuale.")
        if messaggi:
            raise DatiNonValidiError(messaggi)
        self._utenti.aggiorna_password_hash(utente.id, self._hasher.hash(nuova))
        self._conn.commit()

    def password_corretta(self, utente_id: int, password: str) -> bool:
        """
        Conferma della password prima di un'operazione delicata (es. togliere la verifica in due passaggi).
        Returns: True se la password è quella dell'utente.
        """
        utente = self._utenti.leggi_per_id(utente_id)
        if utente is None or len(password or "") > LUNGHEZZA_MASSIMA_PASSWORD:
            return False
        return self._verifica(utente.password_hash, password or "")

    def reimposta_password(self, email: str, nuova: str) -> None:
        """
        Nuova password scelta dallo sviluppatore (comando flask reimposta-password), per quando il
        proprietario l'ha dimenticata: non serve quella attuale.
        Raises: DatiNonValidiError se l'email non è registrata o la password non va bene
        (lunghezza, password comune, ripetitiva o con l'email o il nome del sito).
        """
        utente = self._utente_da_email(email)
        messaggi = self._controlla_nuova_password(nuova, nuova, utente.email)
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
    def _controlla_nuova_password(nuova: str, conferma: str, email: str) -> list[str]:
        """
        Returns: i messaggi di errore sulla nuova password (lunghezza minima e massima, password
        facile da indovinare, conferma); lista vuota se va bene.
        """
        messaggi = []
        if len(nuova or "") < LUNGHEZZA_MINIMA_PASSWORD:
            messaggi.append(f"La nuova password deve avere almeno {LUNGHEZZA_MINIMA_PASSWORD} caratteri.")
        elif len(nuova) > LUNGHEZZA_MASSIMA_PASSWORD:
            messaggi.append(f"La nuova password può avere al massimo {LUNGHEZZA_MASSIMA_PASSWORD} caratteri.")
        else:
            messaggi += _controlla_password_debole(nuova, email)
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


def _controlla_password_debole(password: str, email: str) -> list[str]:
    """
    Controlli del NIST (SP 800-63B) sulle password scelte: non deve essere tra le password comuni
    trapelate, ripetitiva, né contenere il nome del sito o la parte dell'email prima della @.
    Il confronto ignora maiuscole, spazi e segni (es. "Smash Broski!" vale "smashbroski").
    Returns: il messaggio di errore, o lista vuota se la password va bene.
    """
    minuscola = password.lower()
    compatta = re.sub(r"[^a-z0-9]", "", minuscola)
    nome_email = re.sub(r"[^a-z0-9]", "", (email or "").split("@")[0].lower())
    if (minuscola in PASSWORD_COMUNI
            or len(set(minuscola)) < CARATTERI_DIVERSI_MINIMI
            or any(parola in compatta for parola in PAROLE_DEL_SITO)
            or (len(nome_email) >= 4 and nome_email in compatta)):
        return ["Questa password è facile da indovinare (comune, ripetitiva o con il nome del sito "
                "o dell'email): scegline un'altra, per esempio una frase di tre o quattro parole."]
    return []
