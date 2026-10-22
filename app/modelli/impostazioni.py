from dataclasses import dataclass
from urllib.parse import quote_plus

URL_RICERCA_MAPS = "https://www.google.com/maps/search/?api=1&query="
URL_WHATSAPP = "https://wa.me/"


@dataclass
class Impostazioni:
    """
    Dati del locale mostrati nelle pagine (una sola riga nel database).
    """
    nome_locale: str
    indirizzo: str
    telefono: str  # con prefisso internazionale e senza spazi, come serve al link tel:
    email: str
    url_facebook: str
    url_instagram: str
    telefono_di_prova: bool = True  # se vero: scritta "numero di prova" ed escluso dal JSON-LD
    whatsapp: str = ""  # stesso formato del telefono; può essere un cellulare diverso dal fisso
    whatsapp_di_prova: bool = True  # come telefono_di_prova: il numero è un segnaposto
    fuso_orario: str = "Europe/Rome"
    id: int = 1

    def link_maps(self) -> str:
        """
        Link a Google Maps costruito dall'indirizzo, al posto del link breve maps.app.goo.gl
        del sito attuale (AU-NAV10): resta valido e si legge nel codice.
        Returns: l'URL di ricerca di Google Maps con l'indirizzo codificato.
        """
        return URL_RICERCA_MAPS + quote_plus(self.indirizzo)

    def link_whatsapp(self) -> str:
        """
        Link alla chat WhatsApp del locale: wa.me vuole il numero con il prefisso internazionale
        ma senza "+" e senza spazi.
        Returns: l'URL wa.me con le sole cifre del numero WhatsApp.
        """
        return URL_WHATSAPP + "".join(c for c in self.whatsapp if c.isdigit())
