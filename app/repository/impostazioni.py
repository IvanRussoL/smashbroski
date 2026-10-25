from app.modelli.impostazioni import Impostazioni


class ImpostazioniRepository:
    """
    Accesso alla tabella impostazioni, che ha una sola riga (id = 1).
    """

    def __init__(self, connessione):
        self._conn = connessione

    def leggi(self) -> Impostazioni | None:
        """
        Returns: le Impostazioni del locale, oppure None se i dati iniziali non sono stati caricati.
        """
        with self._conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT id, nome_locale, indirizzo, telefono, telefono_di_prova, whatsapp, whatsapp_di_prova, email, "
                "url_facebook, url_instagram, fuso_orario FROM impostazioni WHERE id = 1"
            )
            riga = cur.fetchone()
        if riga is None:
            return None
        riga["telefono_di_prova"] = bool(riga["telefono_di_prova"])
        riga["whatsapp_di_prova"] = bool(riga["whatsapp_di_prova"])
        return Impostazioni(**riga)
