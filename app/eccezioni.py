class SmashBroskiError(Exception):
    """
    Classe base delle eccezioni del progetto: indica una regola di business violata.
    """


class DatiNonValidiError(SmashBroskiError):
    """
    Dati inviati dal proprietario non validi (prezzo, formato, orari...). Contiene tutti i messaggi,
    così il modulo li mostra insieme. Gestione: modulo mostrato di nuovo, codice 400.
    """

    def __init__(self, messaggi: list[str]):
        self.messaggi = messaggi
        super().__init__("; ".join(messaggi))


class NonTrovatoError(SmashBroskiError):
    """
    Dato richiesto inesistente (es. una voce del menù). Gestione: pagina 404.
    """
