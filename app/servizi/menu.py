import re
from dataclasses import dataclass, field

from app.eccezioni import DatiNonValidiError, NonTrovatoError
from app.modelli.menu import Categoria, PrezzoVoce, VoceMenu
from app.repository.menu import MenuRepository

# Euro con la virgola e al massimo due decimali: "7", "7,5", "7,50". Il punto è rifiutato,
# per non confondere i decimali con il separatore delle migliaia.
_FORMATO_PREZZO = re.compile(r"^(\d{1,3})(?:,(\d{1,2}))?$")
PREZZO_MINIMO, PREZZO_MASSIMO = 1, 99999  # 0,01 € e 999,99 €

LUNGHEZZE_MASSIME = {"nome": 100, "descrizione": 255, "edizione": 30, "nota": 255}
POSIZIONE_MASSIMA = 32767  # SMALLINT


def converti_prezzo(testo: str) -> int:
    """
    Converte il prezzo scritto dal proprietario in centesimi: "7" -> 700, "7,5" -> 750, "7,50" -> 750.
    Returns: il prezzo in centesimi, da 1 (0,01 €) a 99999 (999,99 €).
    Raises: DatiNonValidiError se il formato è sbagliato o il prezzo è fuori dai limiti.
    """
    corrispondenza = _FORMATO_PREZZO.match(testo.strip()) if isinstance(testo, str) else None
    if corrispondenza is None:
        raise DatiNonValidiError([
            f"Prezzo «{testo}» non valido: scrivilo in euro con la virgola, es. 7 oppure 7,50."
        ])
    euro, decimali = corrispondenza.group(1), corrispondenza.group(2) or "0"
    centesimi = int(euro) * 100 + int(decimali.ljust(2, "0"))
    if not PREZZO_MINIMO <= centesimi <= PREZZO_MASSIMO:
        raise DatiNonValidiError([f"Prezzo «{testo}» non valido: deve essere tra 0,01 e 999,99 euro."])
    return centesimi


@dataclass
class DatiVoce:
    """
    Dati di una voce così come arrivano dal modulo dell'area proprietario: testi da validare.
    prezzo_unico vuoto se la voce ha prezzi con formato; prezzi_formati è una lista di coppie
    (id del formato, prezzo scritto), con i prezzi vuoti per i formati non offerti.
    posizione vuota: la voce va in fondo alla categoria.
    """
    categoria_id: int | str
    nome: str
    descrizione: str = ""
    edizione: str = ""
    nota: str = ""
    posizione: int | str = ""
    prezzo_unico: str = ""
    prezzi_formati: list[tuple[int | str, str]] = field(default_factory=list)


class MenuService:
    """
    Regole del menù (sezione 3 di PROGETTAZIONE.md): menù pubblico, creazione e modifica delle voci
    con le regole sui prezzi, nascondere e rimostrare. Ogni salvataggio è una transazione.
    """

    def __init__(self, connessione):
        self._conn = connessione
        self._repo = MenuRepository(connessione)

    # --- Lettura ---

    def menu_pubblico(self) -> list[Categoria]:
        """
        Returns: le categorie con almeno una voce visibile, in ordine, ognuna con le sole voci visibili.
        Una categoria con tutte le voci nascoste non compare (né come titolo né nell'indice).
        """
        return [categoria for categoria in self._repo.leggi_menu(solo_attive=True) if categoria.voci]

    def menu_completo(self) -> list[Categoria]:
        """
        Returns: tutte le categorie, anche senza voci, con le voci visibili e nascoste (area proprietario).
        """
        return self._repo.leggi_menu(solo_attive=False)

    def leggi_voce(self, voce_id: int) -> VoceMenu:
        """
        Raises: NonTrovatoError se la voce non esiste.
        """
        voce = self._repo.leggi_voce(voce_id)
        if voce is None:
            raise NonTrovatoError("Voce del menù non trovata.")
        return voce

    def leggi_categoria(self, categoria_id) -> Categoria:
        """
        Returns: la categoria con i suoi formati di prezzo e le sue voci (anche nascoste).
        Raises: NonTrovatoError se la categoria non esiste.
        """
        categoria = self._categoria(categoria_id)
        if categoria is None:
            raise NonTrovatoError("Categoria non trovata.")
        return categoria

    # --- Scrittura ---

    def crea_voce(self, dati: DatiVoce) -> int:
        """
        Valida i dati e salva la voce con i suoi prezzi in una transazione.
        Returns: l'id della nuova voce.
        Raises: DatiNonValidiError con tutti i messaggi; nel database non viene salvato niente.
        """
        voce = self._valida(dati, voce_id=None)
        try:
            voce_id = self._repo.inserisci_voce(voce)
            self._repo.sostituisci_prezzi(voce_id, voce.prezzi)
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        return voce_id

    def modifica_voce(self, voce_id: int, dati: DatiVoce) -> None:
        """
        Valida i dati e salva la voce con i nuovi prezzi (quelli vecchi sono sostituiti) in una
        transazione. La visibilità non cambia.
        Raises: NonTrovatoError se la voce non esiste; DatiNonValidiError con tutti i messaggi.
        """
        esistente = self.leggi_voce(voce_id)
        voce = self._valida(dati, voce_id=voce_id)
        voce.attiva = esistente.attiva
        try:
            self._repo.aggiorna_voce(voce)
            self._repo.sostituisci_prezzi(voce_id, voce.prezzi)
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def imposta_visibilita(self, voce_id: int, attiva: bool) -> None:
        """
        Nasconde (attiva = False) o rimostra (attiva = True) una voce, senza cancellarla.
        Raises: NonTrovatoError se la voce non esiste.
        """
        self.leggi_voce(voce_id)
        self._repo.imposta_attiva(voce_id, attiva)
        self._conn.commit()

    # --- Validazione ---

    def _valida(self, dati: DatiVoce, voce_id: int | None) -> VoceMenu:
        """
        Controlla tutte le regole e raccoglie i messaggi invece di fermarsi al primo errore.
        Returns: la VoceMenu pronta da salvare, con i prezzi in centesimi.
        Raises: DatiNonValidiError.
        """
        messaggi = []
        categoria = self._categoria(dati.categoria_id)
        if categoria is None:
            raise DatiNonValidiError(["Categoria non valida."])

        testi = {nome: (getattr(dati, nome) or "").strip() for nome in LUNGHEZZE_MASSIME}
        if not testi["nome"]:
            messaggi.append("Il nome è obbligatorio.")
        for nome, massimo in LUNGHEZZE_MASSIME.items():
            if len(testi[nome]) > massimo:
                messaggi.append(f"Il campo {nome} può avere al massimo {massimo} caratteri.")
        if testi["nome"] and len(testi["nome"]) <= LUNGHEZZE_MASSIME["nome"] and self._repo.esiste_nome(
            categoria.id, testi["nome"], escludi_voce_id=voce_id
        ):
            messaggi.append(f"Nella categoria {categoria.nome} c'è già una voce chiamata «{testi['nome']}».")

        posizione = self._posizione(dati.posizione, categoria, messaggi)
        prezzi = self._prezzi(dati, categoria, messaggi)

        if messaggi:
            raise DatiNonValidiError(messaggi)
        return VoceMenu(
            categoria_id=categoria.id,
            nome=testi["nome"],
            posizione=posizione,
            descrizione=testi["descrizione"] or None,
            edizione=testi["edizione"] or None,
            nota=testi["nota"] or None,
            prezzi=prezzi,
            id=voce_id,
        )

    def _categoria(self, categoria_id) -> Categoria | None:
        """
        Returns: la categoria con i suoi voci e formati, oppure None se l'id non è valido.
        """
        try:
            categoria_id = int(categoria_id)
        except (TypeError, ValueError):
            return None
        for categoria in self._repo.leggi_menu(solo_attive=False):
            if categoria.id == categoria_id:
                return categoria
        return None

    @staticmethod
    def _posizione(valore, categoria: Categoria, messaggi: list[str]) -> int:
        """
        Returns: la posizione indicata, oppure quella dopo l'ultima voce della categoria se vuota.
        """
        if valore is None or str(valore).strip() == "":
            return max((voce.posizione for voce in categoria.voci), default=0) + 1
        try:
            posizione = int(str(valore).strip())
        except ValueError:
            posizione = 0
        if not 1 <= posizione <= POSIZIONE_MASSIMA:
            messaggi.append("La posizione deve essere un numero intero maggiore di 0.")
        return posizione

    @staticmethod
    def _prezzi(dati: DatiVoce, categoria: Categoria, messaggi: list[str]) -> list[PrezzoVoce]:
        """
        Prezzo unico oppure prezzi con i formati della categoria, mai entrambi; ogni formato al
        massimo una volta; almeno un prezzo.
        Returns: i PrezzoVoce in centesimi (lista parziale se ci sono errori, già segnalati in messaggi).
        """
        formati = {formato.id: formato for formato in categoria.formati}
        prezzo_unico = (dati.prezzo_unico or "").strip()
        con_formato = [(formato_id, (testo or "").strip()) for formato_id, testo in dati.prezzi_formati
                       if (testo or "").strip()]

        if prezzo_unico and con_formato:
            messaggi.append("Indica un prezzo unico oppure i prezzi per formato, non entrambi.")
            return []
        if not prezzo_unico and not con_formato:
            messaggi.append("Indica almeno un prezzo.")
            return []

        prezzi = []
        if prezzo_unico:
            try:
                prezzi.append(PrezzoVoce(converti_prezzo(prezzo_unico)))
            except DatiNonValidiError as errore:
                messaggi.extend(errore.messaggi)
            return prezzi

        visti = set()
        for formato_id, testo in con_formato:
            try:
                formato = formati.get(int(formato_id))
            except (TypeError, ValueError):
                formato = None
            if formato is None:
                messaggi.append(f"Formato di prezzo non valido per la categoria {categoria.nome}.")
                continue
            if formato.id in visti:
                messaggi.append(f"Il formato «{formato.etichetta}» è indicato più di una volta.")
                continue
            visti.add(formato.id)
            try:
                prezzi.append(PrezzoVoce(converti_prezzo(testo), formato_id=formato.id,
                                         etichetta_formato=formato.etichetta))
            except DatiNonValidiError as errore:
                messaggi.extend(f"{formato.etichetta}: {m}" for m in errore.messaggi)
        return prezzi
