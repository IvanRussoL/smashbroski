# Wireframe – SmashBroski Pompei

Wireframe testuale di Home e Menù, su mobile (riferimento 360×800) e desktop (riferimento 1366×768). Indica solo la posizione e il contenuto degli elementi: colori, font e misure precise si decidono con HTML e CSS. Fanno eccezione i due vincoli di colore già decisi: navbar rossa semi-trasparente e contrasto minimo del testo di 4,5:1.

Tra parentesi quadre `[ ]` sono indicati i pulsanti e i link; tra parentesi tonde i riferimenti a requisiti e casi dell'audit.

## Elementi comuni

### Navbar (stile Habita79)

- Fissa in alto, alta circa 56 px, sopra il contenuto. Sfondo rosso del menù al 85% di opacità con sfocatura di ciò che sta sotto (`backdrop-filter: blur()`): con l'85% il testo bianco resta sopra 4,5:1 anche quando sotto c'è una zona bianca.
- A sinistra il logo piccolo (link alla home); a destra tre link: **Menù**, **Orari**, **Contatti**.
- Su mobile i tre link sono brevi e stanno nella riga anche a 360 px: niente menù a scomparsa né JavaScript.
- Il link della pagina aperta ha `aria-current="page"` ed è sottolineato, non solo colorato.
- I titoli raggiunti con i link interni (`#orari`, `#contatti`, `#burger`) hanno `scroll-margin-top` pari all'altezza della navbar, così non finiscono sotto la navbar fissa.

### Footer

- Nome del locale, indirizzo, link **[Privacy e cookie]**, anno (AU-NAV12, RF-08).
- Nessun link visibile all'area riservata: il proprietario apre direttamente `/auth/login`.

## Home – mobile (360×800)

```
┌────────────────────────────────────┐
│ [logo]          Menù Orari Contatti│ ← navbar fissa, rossa 85% + blur
├────────────────────────────────────┤
│                                    │
│        (foto del locale, a         │
│         tutto schermo, con         │
│         sfumatura scura)           │
│                                    │
│          ┌──────────────┐          │
│          │  LOGO GRANDE │          │
│          └──────────────┘          │
│   H1: SmashBroski – Hamburgeria a  │
│              Pompei                │
│                                    │
│   ● Aperto · chiude alle 01:00     │ ← stato apertura (RF-03)
│                                    │
│      [ Guarda il menù ]            │ ← pulsante principale → /menu
│      [ Come arrivare ]             │ ← Google Maps (RF-06)
│                                    │
│               ⌄                    │ ← invito a scorrere
└────────────────────────────────────┘ ← fine hero (min-height: 100dvh)
│ H2: Orari                          │ ← #orari (RF-02)
│ Lunedì    12:00–15:00 · 18:00–01:00│
│ Martedì   Chiuso                   │
│ Mercoledì 12:00–15:00 · 18:00–01:00│ ← oggi: in grassetto + "oggi"
│ Giovedì   12:00–15:00 · 18:00–01:00│
│ Venerdì   12:00–15:00 · 18:00–01:00│
│ Sabato    18:00–02:00              │
│ Domenica  18:00–02:00              │
├────────────────────────────────────┤
│ H2: Contatti                       │ ← #contatti
│ ☎ [+39 081 000 0000] numero di prova│ ← tel: (RF-04)
│ ✉ [info@example.com]               │ ← mailto: (RF-05)
│ ⌖ Vico dei Paninari, 7 - 80045     │
│   Pompei (NA) [Apri in Google Maps]│
│ [ f Facebook ]  [ ◎ Instagram ]    │ ← icone 48×48 con testo (RF-07)
├────────────────────────────────────┤
│ SmashBroski Pompei · Vico dei      │ ← footer
│ Paninari, 7 · [Privacy e cookie]   │
└────────────────────────────────────┘
```

Note:

- **Hero**: `min-height: 100dvh`, non `height: 100vh`. Se lo schermo è basso (375×667, 390×600, orizzontale 667×375, zoom al 200%) l'hero si allunga invece di far uscire il contenuto, e orari e contatti iniziano **sotto** l'hero, nel flusso normale della pagina: nessun blocco in `position: absolute` sopra l'hero (AU-UI01, AU-UI02, AU-UI05, AU-UI06, RNF-01).
- **Logo grande**: altezza limitata in base allo schermo (es. massimo 30% dell'altezza), così in orizzontale non spinge fuori pulsanti e stato di apertura.
- **Foto**: elemento `<picture>` con due tagli, verticale per mobile e orizzontale per desktop; `object-fit: cover`, e su mobile `object-position` sulla parte più pulita della foto. Sfumatura scura dal basso verso l'alto, per leggere testo e pulsanti. Caricamento immediato (mai `lazy`), perché è l'elemento LCP (RNF-04).
- **Stato di apertura**: testo completo, non solo un pallino colorato ("Aperto · chiude alle 01:00", "Chiuso · apre mercoledì alle 12:00").
- **Oggi** negli orari: grassetto più la parola "oggi", non solo il colore. Un turno oltre la mezzanotte resta nel giorno in cui inizia (sezione 3 di PROGETTAZIONE.md).

## Home – desktop (1366×768)

```
┌──────────────────────────────────────────────────────────────────────┐
│ [logo]                                      Menù   Orari   Contatti  │ ← navbar
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────┐                                                      │
│  │ LOGO GRANDE│           (foto del locale a tutta larghezza,        │
│  └────────────┘            sfumatura scura da sinistra verso         │
│  H1: SmashBroski – Hamburgeria   destra: la foto resta visibile      │
│      a Pompei                 a destra)                              │
│  ● Aperto · chiude alle 01:00                                        │
│  [ Guarda il menù ]  [ Come arrivare ]                               │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
        ┌───────────────────────────┐  ┌───────────────────────────┐
        │ H2: Orari                 │  │ H2: Contatti              │
        │ Lunedì   12–15 · 18–01    │  │ ☎ telefono (numero di     │
        │ Martedì  Chiuso           │  │   prova)                  │
        │ ...                       │  │ ✉ email                   │
        │ Domenica 18:00–02:00      │  │ ⌖ indirizzo [Maps]        │
        │                           │  │ [Facebook] [Instagram]    │
        └───────────────────────────┘  └───────────────────────────┘
├──────────────────────────────────────────────────────────────────────┤
│ SmashBroski Pompei · Vico dei Paninari, 7 · [Privacy e cookie]       │
└──────────────────────────────────────────────────────────────────────┘
```

Note:

- Contenuto dell'hero allineato a sinistra, dove la sfumatura è più scura; orari e contatti in due colonne affiancate, con larghezza massima del contenuto di circa 1100 px.
- Sotto i 768 px le due colonne tornano una sotto l'altra, come su mobile.
- Gli orari sul desktop si scrivono per intero (12:00–15:00): nello schizzo sono abbreviati solo per spazio.

## Menù – mobile (360×800)

```
┌────────────────────────────────────┐
│ [logo]          Menù Orari Contatti│ ← "Menù" con aria-current
├────────────────────────────────────┤
│ H1: Menù                           │
│ Prezzi in euro                     │
│                                    │
│ [Starters] [Salad] [Burger]        │ ← indice: link interni,
│ [Kids Menù] [Soft Drinks] [Beers]  │   vanno a capo (RF-11)
│ [The Originals]                    │
├────────────────────────────────────┤
│ H2: Burger                         │ ← #burger
│ Brooo, prova il menù: 1 panino,    │ ← nota della categoria
│ 1 porzione di patatine stick,      │
│ 1 bibita a scelta (Coca-Cola,      │
│ Fanta, Sprite o Acqua).            │
│ ────────────────────────────────── │
│ H3: SMASH BURGER                   │
│ Hamburger, insalata, pomodoro,     │
│ salsa smash                        │
│ Panino single   7,00 €             │ ← ogni prezzo con il suo
│ Panino double   8,50 €             │   formato scritto accanto
│ Menù single    10,00 €             │   (RF-12, AU-NAV04)
│ Menù double    12,00 €             │
│ ────────────────────────────────── │
│ H3: LOS POLLOS CLASSIC             │
│ Pollo croccante, insalata, salsa   │
│ mayo                               │
│ Panino single   7,00 €             │ ← solo i formati esistenti,
│ Menù single    11,00 €             │   niente righe vuote
│ ────────────────────────────────── │
│ [↑ Torna all'indice]               │
├────────────────────────────────────┤
│ H2: The Originals                  │
│ Ortaggio su base stagionale        │
│ H3: SCARULELLA BRO  Winter Edition │ ← etichetta come testo (RF-15)
│ Hamburger 180gr, provola, scarola, │
│ salame a listarelle                │
│ Burger  9,00 €    Menù  13,00 €    │
│ ...                                │
├────────────────────────────────────┤
│ H2: Soft Drinks                    │
│ Acqua 50cl ................ 1,00 € │ ← prezzo unico: nome e prezzo
│ Coca Cola / Fanta / Sprite         │   sulla stessa riga
│ 33cl ...................... 2,00 € │
├────────────────────────────────────┤
│ footer                             │
└────────────────────────────────────┘
```

Note:

- Il menù è una sola pagina scritta dal server; l'indice usa link interni e funziona senza JavaScript (RNF-05, RNF-08).
- Struttura per i lettori di schermo (RF-14, AU-NAV05): `h1` della pagina, `h2` per categoria, `h3` per voce; i prezzi di una voce sono una lista di coppie formato–prezzo (`<dl>`), così il lettore dice "Panino single, 7,00 euro" invece di una serie di numeri.
- Nomi in maiuscolo solo con il CSS: nell'HTML restano "Smash Burger", così la ricerca (Ctrl+F) e la copia funzionano (RF-13).
- Testo dei prezzi almeno grande quanto il testo normale (16 px), leggibile senza zoom a 360 px (RF-10, AU-NAV02).
- Voce con più prezzi su due righe da due (Burger e Menù delle Originals, Single e Menù delle Salad) quando lo spazio basta; altrimenti un prezzo per riga.

## Menù – desktop (1366×768)

```
┌──────────────────────────────────────────────────────────────────────┐
│ [logo]                                      Menù   Orari   Contatti  │
├──────────────────────────────────────────────────────────────────────┤
│        H1: Menù                                                      │
│        [Starters] [Salad] [Burger] [Kids Menù] [Soft Drinks]         │
│        [Beers] [The Originals]                                       │
│                                                                      │
│        H2: Burger                                                    │
│        nota della categoria                                          │
│                                   Panino            Menù             │
│                                single double   single double         │
│        SMASH BURGER             7,00   8,50    10,00  12,00          │
│        Hamburger, insalata, ...                                      │
│        LOS POLLOS CLASSIC       7,00     —     11,00    —            │
│        Pollo croccante, ...                                          │
│        ...                                                           │
│        [↑ Torna all'indice]                                          │
│                                                                      │
│        H2: Soft Drinks                 H2: Beers                     │
│        Acqua 50cl .......... 1,00 €    Nastro Azzurro 33cl . 2,50 €  │
│        ...                             ...                           │
└──────────────────────────────────────────────────────────────────────┘
```

Note:

- Colonna centrale larga al massimo circa 900 px, per non avere righe troppo lunghe.
- Nelle categorie con formati (Burger, The Originals, Salad, Straccetti) i prezzi si allineano in colonne con l'intestazione "a cascata" del PDF: prima Panino e Menù, sotto single e double. L'intestazione è solo visiva (`aria-hidden`): ogni prezzo ha comunque il suo formato nell'HTML, come su mobile. Un formato mancante (Los Pollos double) è una cella con "—".
- Le categorie brevi senza formati (Soft Drinks e Beers) possono stare affiancate in due colonne.

## Pagine non disegnate

- **Privacy e cookie** (`/privacy`): navbar, titolo, testo, footer. Il testo lo forniscono i titolari; finché manca c'è un testo segnaposto marcato come tale.
- **Login** e **area proprietario**: moduli semplici, senza hero; si disegnano quando arriviamo alle rotte di `proprietario`.
