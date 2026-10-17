from app.modelli.menu import Categoria, FormatoPrezzo, PrezzoVoce, VoceMenu

_SELECT_VOCI = (
    "SELECT id, categoria_id, nome, descrizione, edizione, nota, posizione, attiva FROM voci_menu "
)
_SELECT_PREZZI = (
    "SELECT p.id, p.voce_id, p.formato_id, p.prezzo_centesimi, f.etichetta AS etichetta_formato "
    "FROM prezzi_voce p "
    "JOIN voci_menu v ON v.id = p.voce_id "
    "LEFT JOIN formati_prezzo f ON f.id = p.formato_id "
)
_ORDINE_PREZZI = "ORDER BY p.voce_id, f.posizione"


def _voce_da_riga(riga: dict) -> VoceMenu:
    """
    Trasforma una riga di voci_menu in una VoceMenu senza prezzi, convertendo attiva da 0/1 a bool.
    """
    riga["attiva"] = bool(riga["attiva"])
    return VoceMenu(**riga)


class MenuRepository:
    """
    Accesso alle tabelle del menù: categorie, formati_prezzo, voci_menu, prezzi_voce.
    Non fa commit e non applica le regole sui prezzi: lo fa MenuService.
    """

    def __init__(self, connessione):
        self._conn = connessione

    # --- Lettura ---

    def leggi_menu(self, solo_attive: bool = True) -> list[Categoria]:
        """
        Legge tutto il menù con 4 query, qualunque sia il numero di voci (categorie, formati,
        voci, prezzi), e lo ricompone in Python.
        Args: solo_attive, se True esclude le voci nascoste e i loro prezzi.
        Returns: tutte le categorie in ordine di posizione, ognuna con i suoi formati e le sue voci
        (in ordine di posizione), ogni voce con i suoi prezzi (in ordine di formato). Le categorie
        senza voci ci sono comunque: decide il servizio se mostrarle.
        """
        categorie = self.leggi_categorie()
        per_id = {categoria.id: categoria for categoria in categorie}

        filtro = "WHERE attiva = TRUE " if solo_attive else ""
        with self._conn.cursor(dictionary=True) as cur:
            cur.execute(_SELECT_VOCI + filtro + "ORDER BY categoria_id, posizione")
            voci = [_voce_da_riga(riga) for riga in cur.fetchall()]
            cur.execute(_SELECT_PREZZI + ("WHERE v.attiva = TRUE " if solo_attive else "") + _ORDINE_PREZZI)
            righe_prezzi = cur.fetchall()

        voci_per_id = {voce.id: voce for voce in voci}
        for riga in righe_prezzi:
            voci_per_id[riga["voce_id"]].prezzi.append(PrezzoVoce(**riga))
        for voce in voci:
            per_id[voce.categoria_id].voci.append(voce)
        return categorie

    def leggi_categorie(self) -> list[Categoria]:
        """
        Returns: le categorie in ordine di posizione, ognuna con i suoi formati di prezzo
        (in ordine di posizione) e senza voci.
        """
        with self._conn.cursor(dictionary=True) as cur:
            cur.execute("SELECT id, nome, slug, posizione, nota FROM categorie ORDER BY posizione")
            categorie = [Categoria(**riga) for riga in cur.fetchall()]
            cur.execute(
                "SELECT id, categoria_id, etichetta, posizione FROM formati_prezzo "
                "ORDER BY categoria_id, posizione"
            )
            righe_formati = cur.fetchall()
        per_id = {categoria.id: categoria for categoria in categorie}
        for riga in righe_formati:
            per_id[riga["categoria_id"]].formati.append(FormatoPrezzo(**riga))
        return categorie

    def leggi_categoria(self, categoria_id: int) -> Categoria | None:
        """
        Returns: la Categoria con i suoi formati di prezzo, oppure None se non esiste.
        """
        for categoria in self.leggi_categorie():
            if categoria.id == categoria_id:
                return categoria
        return None

    def leggi_voce(self, voce_id: int) -> VoceMenu | None:
        """
        Legge una voce, anche se nascosta, con i suoi prezzi.
        Returns: la VoceMenu, oppure None se non esiste.
        """
        with self._conn.cursor(dictionary=True) as cur:
            cur.execute(_SELECT_VOCI + "WHERE id = %s", (voce_id,))
            riga = cur.fetchone()
            if riga is None:
                return None
            voce = _voce_da_riga(riga)
            cur.execute(_SELECT_PREZZI + "WHERE p.voce_id = %s " + _ORDINE_PREZZI, (voce_id,))
            voce.prezzi = [PrezzoVoce(**r) for r in cur.fetchall()]
        return voce

    def esiste_nome(self, categoria_id: int, nome: str, escludi_voce_id: int | None = None) -> bool:
        """
        Controlla se nella categoria c'è già una voce con quel nome, con lo stesso confronto del
        vincolo UNIQUE del database (senza distinguere maiuscole e accenti).
        Args: escludi_voce_id, la voce in modifica, che può tenere il proprio nome.
        Returns: True se il nome è già usato da un'altra voce della categoria.
        """
        sql = "SELECT 1 FROM voci_menu WHERE categoria_id = %s AND nome = %s"
        parametri = [categoria_id, nome]
        if escludi_voce_id is not None:
            sql += " AND id <> %s"
            parametri.append(escludi_voce_id)
        with self._conn.cursor() as cur:
            cur.execute(sql + " LIMIT 1", tuple(parametri))
            return cur.fetchone() is not None

    # --- Scrittura ---

    def inserisci_voce(self, voce: VoceMenu) -> int:
        """
        Inserisce una voce senza i prezzi (si salvano con sostituisci_prezzi).
        Returns: l'id assegnato da MySQL.
        Raises: mysql.connector.IntegrityError se il nome è già usato nella categoria.
        """
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO voci_menu (categoria_id, nome, descrizione, edizione, nota, posizione, attiva) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (voce.categoria_id, voce.nome, voce.descrizione, voce.edizione, voce.nota,
                 voce.posizione, voce.attiva),
            )
            return cur.lastrowid

    def aggiorna_voce(self, voce: VoceMenu) -> None:
        """
        Salva i campi di una voce esistente, senza i prezzi e senza cambiare attiva
        (si nasconde e rimostra con imposta_attiva).
        Raises: mysql.connector.IntegrityError se il nuovo nome è già usato nella categoria.
        """
        with self._conn.cursor() as cur:
            cur.execute(
                "UPDATE voci_menu SET categoria_id = %s, nome = %s, descrizione = %s, edizione = %s, "
                "nota = %s, posizione = %s WHERE id = %s",
                (voce.categoria_id, voce.nome, voce.descrizione, voce.edizione, voce.nota,
                 voce.posizione, voce.id),
            )

    def sostituisci_prezzi(self, voce_id: int, prezzi: list[PrezzoVoce]) -> None:
        """
        Cancella i prezzi della voce e inserisce quelli nuovi. Il servizio lo chiama dopo aver
        validato i prezzi, nella stessa transazione della voce.
        """
        with self._conn.cursor() as cur:
            cur.execute("DELETE FROM prezzi_voce WHERE voce_id = %s", (voce_id,))
            for prezzo in prezzi:
                cur.execute(
                    "INSERT INTO prezzi_voce (voce_id, formato_id, prezzo_centesimi) VALUES (%s, %s, %s)",
                    (voce_id, prezzo.formato_id, prezzo.prezzo_centesimi),
                )

    def imposta_attiva(self, voce_id: int, attiva: bool) -> None:
        """
        Nasconde (attiva = False) o rimostra (attiva = True) una voce, senza cancellarla.
        """
        with self._conn.cursor() as cur:
            cur.execute("UPDATE voci_menu SET attiva = %s WHERE id = %s", (attiva, voce_id))
