"""
Disegna il logo di SmashBroski in SVG: mascotte e scritta, con il testo convertito in tracciati.
Si esegue solo in sviluppo, quando si vuole cambiare il logo.

Uso, dalla cartella del progetto:
    pip install fonttools brotli
    python strumenti/logo/genera_logo.py

Scrive strumenti/logo/logo.svg. Per il sito: esportare l'SVG in PNG trasparente largo almeno
1920 px (browser o Inkscape), salvarlo come logo.png nella cartella degli originali e lanciare
strumenti/prepara_immagini.py.
"""
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

CARTELLA = Path(__file__).resolve().parent
FONT = CARTELLA.parent.parent / "app" / "static" / "fonts" / "archivo-black-latin-400.woff2"

BLU, CREMA, ROSSO = "#0963AD", "#FFFAF0", "#B00C36"
# Contorno della mascotte: stesso tratto blu arrotondato per tutte le parti.
TRATTO = f'stroke="{BLU}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"'


def testo(scritta: str, x: float, y: float, corpo: float, spaziatura: float = 0, inclinazione: float = 0) -> str:
    """
    Converte la scritta in tracciati SVG, centrata su x con la linea di base su y,
    così il logo non dipende da un font installato.

    Returns: il valore dell'attributo d del tracciato.
    """
    font = TTFont(FONT)
    glifi = font.getGlyphSet()
    nomi = [font.getBestCmap()[ord(carattere)] for carattere in scritta]
    scala = corpo / font["head"].unitsPerEm
    larghezza = sum(glifi[nome].width * scala for nome in nomi) + spaziatura * (len(nomi) - 1)
    penna = SVGPathPen(glifi)
    cursore = x - larghezza / 2
    for nome in nomi:
        # Asse y verso il basso come in SVG; l'inclinazione dà il corsivo.
        glifi[nome].draw(TransformPen(penna, (scala, 0, inclinazione * scala, -scala, cursore, y)))
        cursore += glifi[nome].width * scala + spaziatura
    return penna.getCommands()


def logo() -> str:
    """
    Returns: il documento SVG del logo, 480x427 come logo-hero.webp: la mascotte (panino con il
    berretto da sci del "-ski" e la spatola dello smash), il nome e la riga "SMASH BURGER · POMPEI".
    """
    s = TRATTO
    m = []
    m.append(f'<ellipse cx="240" cy="266" rx="112" ry="11" fill="{BLU}"/>')
    # gambe e scarpe
    for gx in (208, 272):
        m.append(f'<path d="M{gx-11},222 V250 M{gx+11},222 V250" {s} fill="none"/>')
        m.append(f'<path d="M{gx-20},262 C{gx-22},248 {gx+18},244 {gx+24},256 C{gx+26},263 {gx-18},266 {gx-20},262 Z" fill="{CREMA}" {s}/>')
    # pane sotto
    m.append(f'<path d="M150,200 H330 C334,226 312,236 290,236 H190 C168,236 146,226 150,200 Z" fill="{CREMA}" {s}/>')
    # carne schiacciata (smash): bordo irregolare
    m.append(f'<path d="M138,184 C150,176 170,182 188,177 C210,172 232,180 254,175 C278,170 300,179 322,175 C336,173 346,180 344,190 C346,200 334,206 318,204 C296,208 270,201 246,206 C222,210 198,202 176,206 C156,208 136,202 138,184 Z" fill="{BLU}" {s}/>')
    m.append(f'<path d="M170,191 h16 M214,193 h20 M262,190 h14 M298,193 h18" stroke="{CREMA}" stroke-width="4" stroke-linecap="round"/>')
    # formaggio che cola
    m.append(f'<path d="M146,174 H334 L322,184 L314,198 L306,184 L262,184 L252,202 L242,184 L196,184 L186,196 L176,184 L156,184 Z" fill="{CREMA}" {s}/>')
    # pane sopra
    m.append(f'<path d="M134,172 C130,104 182,70 240,70 C298,70 350,104 346,172 Z" fill="{CREMA}" {s}/>')
    # sesamo ai lati del berretto
    for (sx, sy, r) in ((160, 122, -30), (322, 124, 30), (150, 148, -10), (332, 150, 10)):
        m.append(f'<ellipse cx="{sx}" cy="{sy}" rx="6" ry="3.2" transform="rotate({r} {sx} {sy})" fill="{BLU}"/>')
    # faccia: occhi felici, sorriso, guance
    m.append(f'<path d="M198,136 q10,-12 20,0 M262,136 q10,-12 20,0" {s} fill="none"/>')
    m.append(f'<path d="M214,150 q26,26 52,0 Z" fill="{BLU}" {s}/>')
    m.append(f'<path d="M226,158 q14,8 28,0" stroke="{ROSSO}" stroke-width="5" stroke-linecap="round" fill="none"/>')
    m.append(f'<ellipse cx="186" cy="152" rx="9" ry="5" fill="{ROSSO}" opacity=".55"/><ellipse cx="294" cy="152" rx="9" ry="5" fill="{ROSSO}" opacity=".55"/>')
    # berretto da sci (il "-ski") con risvolto a righe e pompon
    m.append(f'<path d="M172,108 C172,62 204,40 240,40 C276,40 308,62 308,108 Z" fill="{ROSSO}" {s}/>')
    m.append(f'<path d="M222,46 C226,64 226,86 224,104 M258,46 C254,64 254,86 256,104" stroke="{CREMA}" stroke-width="4" stroke-linecap="round" fill="none" opacity=".7"/>')
    m.append(f'<rect x="164" y="98" width="152" height="22" rx="11" fill="{CREMA}" {s}/>')
    m.append(f'<path d="M186,104 v10 M206,104 v10 M226,104 v10 M246,104 v10 M266,104 v10 M286,104 v10" stroke="{ROSSO}" stroke-width="6" stroke-linecap="round"/>')
    m.append(f'<circle cx="240" cy="30" r="15" fill="{CREMA}" {s}/>')
    # braccio sinistro sul fianco
    m.append(f'<path d="M138,150 C118,154 110,170 118,184" {s} fill="none"/><circle cx="122" cy="190" r="10" fill="{CREMA}" {s}/>')
    # braccio destro alzato con la spatola
    m.append(f'<path d="M342,150 C364,146 374,124 378,102" {s} fill="none"/>')
    m.append(f'<circle cx="379" cy="98" r="11" fill="{CREMA}" {s}/>')
    m.append(f'<path d="M383,88 L394,58" stroke="{BLU}" stroke-width="9" stroke-linecap="round"/>')
    m.append(f'<path d="M384,56 L404,30 L428,46 L404,70 Z" fill="{CREMA}" {s}/>')
    m.append(f'<path d="M400,46 l10,-8 M406,54 l10,-8" stroke="{BLU}" stroke-width="4" stroke-linecap="round"/>')
    mascotte = "\n  ".join(m)
    nome = testo("SmashBroski", 236, 352, 60, spaziatura=-0.5, inclinazione=0.2)
    sottotitolo = testo("SMASH BURGER · POMPEI", 240, 404, 19, spaziatura=3.2)
    return "\n".join([
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 427" width="480" height="427">',
        f'<g transform="translate(0 0)">\n  {mascotte}\n</g>',
        f'<path d="{nome}" fill="{CREMA}"/>',
        f'<path d="{sottotitolo}" fill="{CREMA}" opacity=".9"/>',
        "</svg>",
    ])


if __name__ == "__main__":
    (CARTELLA / "logo.svg").write_text(logo(), encoding="utf-8")
    print("logo.svg scritto")
