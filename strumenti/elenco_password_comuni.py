"""
Rigenera app/dati/password_comuni.txt dagli elenchi di SecLists (https://github.com/danielmiessler/SecLists,
licenza MIT): tiene le password tra 15 e 128 caratteri, in minuscolo, senza doppioni.

Uso: python strumenti/elenco_password_comuni.py ELENCO1.txt [ELENCO2.txt ...]
"""
import sys
from pathlib import Path

DESTINAZIONE = Path(__file__).resolve().parent.parent / "app" / "dati" / "password_comuni.txt"
INTESTAZIONE = (
    "# Password comuni di almeno 15 caratteri, rifiutate da AuthService (NIST SP 800-63B: elenco di password note).\n"
    "# Fonte: SecLists (licenza MIT), file Passwords/Common-Credentials/100k-most-used-passwords-NCSC.txt\n"
    "# e xato-net-10-million-passwords-1000000.txt, filtrate a 15-128 caratteri, in minuscolo.\n"
    "# Rigenerare con strumenti/elenco_password_comuni.py. Le righe che iniziano con # sono commenti.\n"
)


def main(percorsi: list[str]) -> None:
    password = set()
    for percorso in percorsi:
        for riga in Path(percorso).read_text(encoding="utf-8", errors="ignore").splitlines():
            riga = riga.strip().lower()
            if 15 <= len(riga) <= 128 and riga.isascii() and riga.isprintable() and not riga.startswith(("#", "$hex[")):
                password.add(riga)
    DESTINAZIONE.write_text(INTESTAZIONE + "\n".join(sorted(password)) + "\n", encoding="utf-8")
    print(f"{len(password)} password scritte in {DESTINAZIONE}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
