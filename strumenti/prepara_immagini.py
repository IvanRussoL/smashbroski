"""
Prepara le immagini del sito con Pillow: le converte in WebP e le ridimensiona.
Si esegue solo in sviluppo; il sito non elabora immagini.

Uso, dalla cartella del progetto:
    python strumenti/prepara_immagini.py <cartella con gli originali>

Originali attesi nella cartella (fuori da Git):
    Burger.png          logo del locale (anche per il motivo di piccoli loghi dello sfondo)
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
# Motivo dello sfondo animato di Menù e Orari e contatti: il personaggio del logo (senza scritta)
# in due tinte tenui, rossa e blu, affiancate in una mattonella che si ripete in orizzontale.
# Misure in pixel CSS; il file è a doppia densità.
MOTIVO = "motivo-loghi.webp"
CELLA_MOTIVO = (96, 84)
ALTEZZA_PERSONAGGIO = 56
# (colore delle linee, colore del riempimento) per ogni tinta, molto vicini al fondo crema #FFFAF0.
TINTE_MOTIVO = [((232, 190, 199), (247, 225, 228)), ((196, 216, 236), (228, 237, 246))]
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


def _ritaglia_personaggio(logo: Image.Image) -> Image.Image:
    """
    Returns: solo il personaggio del logo, cioè la parte sopra la prima riga del tutto trasparente
    (sotto c'è la scritta "SmashBroski").
    """
    alfa = logo.getchannel("A")
    larghezza, altezza = logo.size
    for y in range(1, altezza):
        if alfa.crop((0, y, larghezza, y + 1)).getextrema()[1] == 0:
            return logo.crop(logo.crop((0, 0, larghezza, y)).getbbox())
    return logo


def _ricolora(personaggio: Image.Image, linee: tuple, riempimento: tuple) -> Image.Image:
    """
    Ricolora il personaggio in una tinta: le parti scure (contorni blu) prendono il colore delle linee,
    quelle chiare (riempimento crema) il colore del riempimento; la trasparenza resta quella originale.
    """
    luminosita = personaggio.convert("L")
    minimo, massimo = luminosita.getextrema()
    scala = max(massimo - minimo, 1)
    tavolozza = []
    for canale in range(3):
        tavolozza += [round(linee[canale] + (riempimento[canale] - linee[canale]) * max(0, valore - minimo) / scala)
                      for valore in range(256)]
    rosso = luminosita.point(tavolozza[0:256])
    verde = luminosita.point(tavolozza[256:512])
    blu = luminosita.point(tavolozza[512:768])
    return Image.merge("RGBA", (rosso, verde, blu, personaggio.getchannel("A")))


def prepara_motivo(originale: Path) -> None:
    """
    Crea la mattonella del motivo: un personaggio per tinta, centrato nella sua cella, fondo trasparente.
    """
    densita = 2
    cella_l, cella_a = CELLA_MOTIVO[0] * densita, CELLA_MOTIVO[1] * densita
    with Image.open(originale) as logo:
        personaggio = _ritaglia_personaggio(logo.convert("RGBA"))
        altezza = ALTEZZA_PERSONAGGIO * densita
        larghezza = round(personaggio.width * altezza / personaggio.height)
        personaggio = personaggio.resize((larghezza, altezza), Image.Resampling.LANCZOS)
        mattonella = Image.new("RGBA", (cella_l * len(TINTE_MOTIVO), cella_a), (0, 0, 0, 0))
        for indice, (linee, riempimento) in enumerate(TINTE_MOTIVO):
            colorato = _ricolora(personaggio, linee, riempimento)
            x = indice * cella_l + (cella_l - larghezza) // 2
            mattonella.alpha_composite(colorato, (x, (cella_a - altezza) // 2))
        mattonella.save(CARTELLA_USCITA / MOTIVO, "WEBP", quality=QUALITA_LOGO, alpha_quality=100, method=6)
        print(f"{MOTIVO}: {mattonella.width}x{mattonella.height}")


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
        prepara_motivo(cartella / "Burger.png")
        trovato = True
    if (cartella / "hero.jpg").exists():
        prepara_hero(cartella / "hero.jpg")
        trovato = True
    if not trovato:
        sys.exit(f"Nessun originale trovato in {cartella}.")


if __name__ == "__main__":
    main()
