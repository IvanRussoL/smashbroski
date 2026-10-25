from dataclasses import dataclass
from datetime import datetime


@dataclass
class Utente:
    """
    Account dell'area riservata. Esiste un solo ruolo, il proprietario.
    """
    email: str
    password_hash: str
    attivo: bool = True
    creato_il: datetime | None = None  # in UTC, scritto da MySQL
    id: int | None = None
    # Verifica in due passaggi: segreto TOTP cifrato (mai in chiaro), attiva solo dopo il primo codice giusto.
    totp_segreto: str | None = None
    totp_attivo: bool = False
    totp_ultimo_passo: int | None = None
