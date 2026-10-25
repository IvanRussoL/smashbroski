import base64
import hmac
import re
import secrets
from datetime import UTC, datetime

import pyotp
import qrcode
import qrcode.image.svg
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from app.eccezioni import DatiNonValidiError, NonTrovatoError
from app.modelli.utente import Utente
from app.repository.codici_riserva import CodiciRiservaRepository
from app.repository.utente import UtenteRepository

# Codici TOTP (RFC 6238) di 6 cifre che cambiano ogni 30 secondi, come Google Authenticator.
# Si accetta anche il codice dell'intervallo prima e di quello dopo, per piccole differenze di orologio.
FINESTRA_PASSI = 1
NOME_NEL_TELEFONO = "SmashBroski Pompei"
NUMERO_CODICI_RISERVA = 10
# Senza lettere e cifre che si confondono (l/1, o/0, i): 10 caratteri ≈ 49 bit, impossibili da indovinare in 5 tentativi al minuto.
_ALFABETO_RISERVA = "abcdefghjkmnpqrstuvwxyz23456789"

MESSAGGIO_CODICE_ERRATO = "Il codice non è corretto o è scaduto."

_HASHER = PasswordHasher()


def _chiave_cifratura(chiave_segreta: str) -> bytes:
    """
    Chiave Fernet (AES con HMAC) per cifrare i segreti TOTP nel database, ricavata dalla SECRET_KEY
    con HKDF: una copia del database da sola non basta a generare i codici.
    """
    chiave = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"smashbroski totp").derive(
        chiave_segreta.encode()
    )
    return base64.urlsafe_b64encode(chiave)


def _normalizza_riserva(codice: str) -> str:
    """
    Returns: il codice di riserva in minuscolo, senza spazi e trattini (si può scrivere come si vuole).
    """
    return "".join(c for c in (codice or "").lower() if c.isalnum())


def codice_qr_svg(testo: str) -> str:
    """
    Returns: il codice QR del testo come SVG da mettere nella pagina (niente immagini esterne, CSP rispettata).
    """
    immagine = qrcode.make(testo, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=2)
    svg = immagine.to_string(encoding="unicode")
    # Le misure le decide il CSS (.codice-qr svg): via width e height in millimetri.
    return re.sub(r'^<svg width="[^"]*" height="[^"]*"', '<svg role="img" aria-label="Codice QR da inquadrare"', svg)


class DuePassaggiService:
    """
    Verifica in due passaggi del proprietario: dopo la password, un codice di 6 cifre dall'app del
    telefono (Google Authenticator o simili) oppure un codice di riserva.
    """

    def __init__(self, connessione, chiave_segreta: str):
        self._conn = connessione
        self._utenti = UtenteRepository(connessione)
        self._riserva = CodiciRiservaRepository(connessione)
        self._fernet = Fernet(_chiave_cifratura(chiave_segreta))

    def prepara(self, utente_id: int) -> None:
        """
        Primo passo dell'attivazione: crea un segreto nuovo (160 bit) e lo salva cifrato, ancora
        non attivo; il QR si legge poi con attivazione_in_corso().
        Raises: DatiNonValidiError se la verifica è già attiva.
        """
        utente = self._utente(utente_id)
        if utente.totp_attivo:
            raise DatiNonValidiError(["La verifica in due passaggi è già attiva."])
        segreto = pyotp.random_base32()
        self._utenti.salva_totp(utente_id, self._cifra(segreto), attivo=False)
        self._conn.commit()

    def attivazione_in_corso(self, utente_id: int) -> tuple[str, str] | None:
        """
        Returns: indirizzo otpauth:// (per il QR) e segreto (da scrivere a mano se il QR non si
        legge) durante l'attivazione; None se la verifica è già attiva o non è iniziata.
        """
        utente = self._utente(utente_id)
        if utente.totp_attivo or not utente.totp_segreto:
            return None
        segreto = self._decifra(utente.totp_segreto)
        return pyotp.TOTP(segreto).provisioning_uri(name=utente.email, issuer_name=NOME_NEL_TELEFONO), segreto

    def conferma(self, utente_id: int, codice: str, adesso: datetime | None = None) -> list[str]:
        """
        Secondo passo dell'attivazione: il codice dell'app prova che il telefono è configurato.
        Returns: i 10 codici di riserva, da mostrare una volta sola (nel database solo gli hash).
        Raises: DatiNonValidiError se l'attivazione non è iniziata o il codice è sbagliato.
        """
        utente = self._utente(utente_id)
        if utente.totp_attivo or not utente.totp_segreto:
            raise DatiNonValidiError(["Attivazione non iniziata: premi di nuovo \"Attiva\"."])
        passo = self._passo_valido(utente, codice, adesso)
        if passo is None:
            raise DatiNonValidiError([MESSAGGIO_CODICE_ERRATO])
        self._utenti.salva_totp(utente_id, utente.totp_segreto, attivo=True)
        self._utenti.aggiorna_ultimo_passo(utente_id, passo)
        codici = self._nuovi_codici_riserva(utente_id)
        self._conn.commit()
        return codici

    def verifica(self, utente: Utente, codice: str, adesso: datetime | None = None) -> bool:
        """
        Controllo al login: codice dell'app (6 cifre, mai due volte lo stesso) oppure un codice di
        riserva non ancora usato, che da quel momento non vale più.
        Returns: True se il codice è valido.
        """
        if not utente.totp_attivo:
            return False
        codice = (codice or "").strip().replace(" ", "")
        if len(codice) == 6 and codice.isdigit():
            passo = self._passo_valido(utente, codice, adesso)
            if passo is None:
                return False
            self._utenti.aggiorna_ultimo_passo(utente.id, passo)
            self._conn.commit()
            return True
        return self._usa_codice_riserva(utente.id, codice, adesso)

    def codici_riserva_rimasti(self, utente_id: int) -> int:
        """
        Returns: quanti codici di riserva non usati restano.
        """
        return len(self._riserva.leggi_non_usati(utente_id))

    def rigenera_codici_riserva(self, utente_id: int) -> list[str]:
        """
        Sostituisce tutti i codici di riserva (i vecchi non valgono più).
        Returns: i 10 codici nuovi, da mostrare una volta sola.
        """
        if not self._utente(utente_id).totp_attivo:
            raise DatiNonValidiError(["La verifica in due passaggi non è attiva."])
        codici = self._nuovi_codici_riserva(utente_id)
        self._conn.commit()
        return codici

    def disattiva(self, utente_id: int) -> None:
        """
        Toglie la verifica in due passaggi: cancella segreto e codici di riserva. La rotta chiede
        prima la password; lo sviluppatore usa il comando disattiva-due-passaggi.
        """
        self._utente(utente_id)
        self._utenti.salva_totp(utente_id, None, attivo=False)
        self._riserva.cancella(utente_id)
        self._conn.commit()

    def _utente(self, utente_id: int) -> Utente:
        utente = self._utenti.leggi_per_id(utente_id)
        if utente is None:
            raise NonTrovatoError("Utente non trovato.")
        return utente

    def _passo_valido(self, utente: Utente, codice: str, adesso: datetime | None) -> int | None:
        """
        Returns: l'intervallo di 30 secondi del codice, se il codice è giusto per l'intervallo
        attuale, quello prima o quello dopo ed è successivo all'ultimo usato; altrimenti None.
        """
        codice = (codice or "").strip().replace(" ", "")
        if len(codice) != 6 or not codice.isdigit():
            return None
        totp = pyotp.TOTP(self._decifra(utente.totp_segreto))
        attuale = totp.timecode(adesso or datetime.now(UTC))
        for passo in range(attuale - FINESTRA_PASSI, attuale + FINESTRA_PASSI + 1):
            if utente.totp_ultimo_passo is not None and passo <= utente.totp_ultimo_passo:
                continue
            if hmac.compare_digest(totp.generate_otp(passo), codice):
                return passo
        return None

    def _usa_codice_riserva(self, utente_id: int, codice: str, adesso: datetime | None) -> bool:
        normalizzato = _normalizza_riserva(codice)
        if len(normalizzato) != 10:
            return False
        for codice_id, codice_hash in self._riserva.leggi_non_usati(utente_id):
            try:
                _HASHER.verify(codice_hash, normalizzato)
            except (VerificationError, InvalidHashError):
                continue
            self._riserva.segna_usato(codice_id, (adesso or datetime.now(UTC)).replace(tzinfo=None))
            self._conn.commit()
            return True
        return False

    def _nuovi_codici_riserva(self, utente_id: int) -> list[str]:
        codici = []
        for _ in range(NUMERO_CODICI_RISERVA):
            grezzo = "".join(secrets.choice(_ALFABETO_RISERVA) for _ in range(10))
            codici.append(f"{grezzo[:5]}-{grezzo[5:]}")
        self._riserva.sostituisci(utente_id, [_HASHER.hash(_normalizza_riserva(c)) for c in codici])
        return codici

    def _cifra(self, segreto: str) -> str:
        return self._fernet.encrypt(segreto.encode()).decode()

    def _decifra(self, segreto_cifrato: str) -> str:
        """
        Raises: DatiNonValidiError se il segreto non si decifra (SECRET_KEY cambiata): va riattivata.
        """
        try:
            return self._fernet.decrypt(segreto_cifrato.encode()).decode()
        except InvalidToken:
            raise DatiNonValidiError(
                ["La verifica in due passaggi va riattivata (chiave del sito cambiata): chiedi allo sviluppatore."]
            )
