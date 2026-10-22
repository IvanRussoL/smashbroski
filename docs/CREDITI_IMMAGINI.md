# Crediti delle immagini e dei caratteri

Immagini usate nel prototipo, con provenienza e stato. Gli originali stanno fuori dal repository (`materiale_grafico/`); nel repository ci sono solo i file WebP preparati da `strumenti/prepara_immagini.py`.

| File nel sito | Originale | Provenienza | Autore | Data | Stato |
|---|---|---|---|---|---|
| `app/static/img/logo-hero.webp`, `logo-navbar.webp` | `Burger.png` | Sito attuale del locale: https://smashbroski.example/wp-content/uploads/2024/09/Burger.png | SmashBroski Pompei (marchio del locale) | 2026-10-17 | Usato per la proposta ai titolari; permesso da chiedere prima della pubblicazione |
| `app/static/img/hero-verticale.webp`, `hero-orizzontale.webp`, `hero-orizzontale-piccola.webp` | `hero.jpg` | Pexels: https://www.pexels.com/it-it/foto/legno-tavolo-dentro-interno-11229762/ (licenza Pexels, uso gratuito) | Mathias Reding (https://www.pexels.com/it-it/@matreding/) | 2026-10-18 | Foto di lavoro, non è il locale: da sostituire con una foto del locale prima della pubblicazione |

## Caratteri

Salvati nel sito (`app/static/fonts/`), senza servizi esterni; la licenza di ognuno è nel file accanto.

| File nel sito | Carattere | Autori | Licenza | Uso |
|---|---|---|---|---|
| `archivo-black-latin-400.woff2` | Archivo Black | The Archivo Black Project Authors (https://github.com/Omnibus-Type/ArchivoBlack) | SIL Open Font License 1.1 (`OFL-Archivo-Black.txt`) | Nomi delle voci, prezzi e indice del menù |
| `archivo-latin-variabile.woff2` | Archivo (variabile: pesi 100–900, larghezze 62–125%) | The Archivo Project Authors (https://github.com/Omnibus-Type/Archivo) | SIL Open Font License 1.1 (`OFL-Archivo.txt`) | Testo normale e titoli (larghezza 125%, peso 900) di tutto il sito |

File WebFont del sottoinsieme latino presi dai pacchetti npm `@fontsource/archivo-black` e `@fontsource-variable/archivo` (versione 5, file con gli assi peso e larghezza).
