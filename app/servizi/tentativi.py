import hmac
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from app.repository.tentativi import TentativiRepository

# Al massimo 5 tentativi sbagliati al minuto per indirizzo IP e per ambito, poi 429 fino a quando
# il più vecchio dei 5 esce dalla finestra (al massimo un minuto). Nessun blocco permanente (OWASP).
LIMITE_TENTATIVI = 5
FINESTRA = timedelta(minutes=1)
# I tentativi più vecchi di così si cancellano: per contare basta l'ultimo minuto.
CONSERVAZIONE = timedelta(hours=1)

AMBITO_LOGIN = "login"
AMBITO_CAMBIO_PASSWORD = "password"


def adesso_utc() -> datetime:
    """
    Returns: l'istante attuale in UTC senza fuso, come le colonne DATETIME del database.
    """
    return datetime.now(UTC).replace(tzinfo=None)


class TentativiService:
    """
    Limite ai tentativi sbagliati di login e di cambio password. I conteggi stanno nel database,
    quindi valgono per tutti i processi del server e non si azzerano a un riavvio.
    """

    def __init__(self, connessione, chiave_segreta: str):
        self._conn = connessione
        self._tentativi = TentativiRepository(connessione)
        self._chiave = chiave_segreta.encode()

    def impronta(self, ip: str) -> str:
        """
        Returns: HMAC-SHA256 dell'IP con la SECRET_KEY (64 caratteri esadecimali). L'IP in chiaro
        non si salva: l'impronta basta per contare e non permette di risalire all'indirizzo
        senza la chiave.
        """
        return hmac.new(self._chiave, (ip or "").encode(), sha256).hexdigest()

    def bloccato(self, ambito: str, ip: str, adesso: datetime | None = None) -> bool:
        """
        Returns: True se quell'IP ha già fatto LIMITE_TENTATIVI tentativi sbagliati nell'ambito
        nell'ultimo minuto.
        """
        adesso = adesso or adesso_utc()
        return self._tentativi.conta_dal(ambito, self.impronta(ip), adesso - FINESTRA) >= LIMITE_TENTATIVI

    def registra_fallito(self, ambito: str, ip: str, adesso: datetime | None = None) -> None:
        """
        Registra un tentativo sbagliato e cancella quelli più vecchi di un'ora, con commit:
        il tentativo deve contare anche se la richiesta finisce con un errore.
        """
        adesso = adesso or adesso_utc()
        self._tentativi.cancella_prima_di(adesso - CONSERVAZIONE)
        self._tentativi.inserisci(ambito, self.impronta(ip), adesso)
        self._conn.commit()
