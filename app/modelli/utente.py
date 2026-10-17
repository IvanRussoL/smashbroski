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
