"""
Prepara le immagini del sito con Pillow: le converte in WebP e le ridimensiona.
Si esegue solo in sviluppo; il sito non elabora immagini.

Uso, dalla cartella del progetto:
    python strumenti/prepara_immagini.py <cartella con gli originali>

Originali attesi nella cartella (fuori da Git):
    Burger.png          logo del locale
    hero.jpg            foto del locale per l'hero, entrata o sala (facoltativa finché manca)
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

CARTELLA_USCITA = Path(__file__).resolve().parent.parent / "app" / "static" / "img"

# (nome del file, larghezza) per il logo: grande nell'hero, piccolo nella navbar (doppia densità).
FORMATI_LOGO = [("logo-hero.webp", 480), ("logo-navbar.webp", 96)]
# (nome del file, larghezza, altezza) per la foto dell'hero: taglio verticale per i telefoni,
# orizzontale per tablet e computer.
FORMATI_HERO = [
    ("hero-verticale.webp", 900, 1600),
    ("hero-orizzontale.webp", 1920, 1080),
    ("hero-orizzontale-piccola.webp", 1280, 720),
]
QUALITA_FOTO = 72
QUALITA_LOGO = 90


def prepara_logo(originale: Path) -> None:
    """
    Ridimensiona il logo mantenendo le proporzioni e la trasparenza, in WebP ad alta qualità (contorni del logo nitidi, file leggero).
    """
    with Image.open(originale) as logo:
        logo = logo.convert("RGBA")
        for nome, larghezza in FORMATI_LOGO:
            altezza = round(logo.height * larghezza / logo.width)
            ridotto = logo.resize((larghezza, altezza), Image.Resampling.LANCZOS)
            ridotto.save(CARTELLA_USCITA / nome, "WEBP", quality=QUALITA_LOGO, alpha_quality=100, method=6)
            print(f"{nome}: {larghezza}x{altezza}")


def prepara_hero(originale: Path) -> None:
    """
    Taglia la foto al centro nelle proporzioni richieste e la salva in WebP. L'orientamento
    scritto dalla fotocamera (EXIF) viene applicato prima del taglio; i metadati non vengono copiati.
    """
    with Image.open(originale) as foto:
        foto = ImageOps.exif_transpose(foto).convert("RGB")
        for nome, larghezza, altezza in FORMATI_HERO:
            tagliata = ImageOps.fit(foto, (larghezza, altezza), Image.Resampling.LANCZOS)
            tagliata.save(CARTELLA_USCITA / nome, "WEBP", quality=QUALITA_FOTO, method=6)
            print(f"{nome}: {larghezza}x{altezza}")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    cartella = Path(sys.argv[1])
    CARTELLA_USCITA.mkdir(parents=True, exist_ok=True)
    trovato = False
    if (cartella / "Burger.png").exists():
        prepara_logo(cartella / "Burger.png")
        trovato = True
    if (cartella / "hero.jpg").exists():
        prepara_hero(cartella / "hero.jpg")
        trovato = True
    if not trovato:
        sys.exit(f"Nessun originale trovato in {cartella}.")


if __name__ == "__main__":
    main()
