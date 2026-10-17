from dataclasses import dataclass, field


@dataclass
class FormatoPrezzo:
    """
    Formato di prezzo di una categoria, come una colonna del PDF (es. "Panino single hamb.").
    """
    categoria_id: int
    etichetta: str
    posizione: int
    id: int | None = None


@dataclass
class PrezzoVoce:
    """
    Un prezzo di una voce. Senza formato è il prezzo unico della voce.
    """
    prezzo_centesimi: int
    formato_id: int | None = None
    etichetta_formato: str | None = None  # letta da formati_prezzo, per mostrarla senza altre query
    voce_id: int | None = None
    id: int | None = None


@dataclass
class VoceMenu:
    """
    Piatto o bevanda del menù, con i suoi prezzi. Una voce nascosta ha attiva = False.
    """
    categoria_id: int
    nome: str
    posizione: int
    descrizione: str | None = None
    edizione: str | None = None  # es. "Winter Edition": solo da mostrare
    nota: str | None = None
    attiva: bool = True
    prezzi: list[PrezzoVoce] = field(default_factory=list)
    id: int | None = None

    def ha_prezzo_unico(self) -> bool:
        """
        Returns: True se la voce ha un solo prezzo senza formato (es. le bevande).
        """
        return len(self.prezzi) == 1 and self.prezzi[0].formato_id is None


@dataclass
class Categoria:
    """
    Categoria del menù (le 7 del PDF), con i suoi formati di prezzo e le sue voci.
    """
    nome: str
    slug: str  # per i link interni della pagina, es. /menu#kids-menu
    posizione: int
    nota: str | None = None
    formati: list[FormatoPrezzo] = field(default_factory=list)
    voci: list[VoceMenu] = field(default_factory=list)
    id: int | None = None
