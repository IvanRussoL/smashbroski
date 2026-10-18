# Wireframe – SmashBroski Pompei

Wireframe testuale di Home, Menù e Orari e contatti, su mobile (riferimento 360×800) e desktop (riferimento 1366×768). Indica solo la posizione e il contenuto degli elementi: colori, font e misure precise si decidono con HTML e CSS. Fanno eccezione i vincoli di colore già decisi: navbar di vetro rosso, fascia "Dove siamo" nel blu del logo, footer rosso e contrasto minimo del testo di 4,5:1.

Versione aggiornata il 18 ottobre 2026 alla grafica 2 (DEVLOG, voce "Navbar stile Habita79, ora di Pompei, pagina Orari e contatti, sfondo di loghi, doppio footer"): la home è solo l'hero, orari e contatti sono nella pagina `/info`.

Tra parentesi quadre `[ ]` sono indicati i pulsanti e i link; tra parentesi tonde i riferimenti a requisiti e casi dell'audit.

## Elementi comuni

### Navbar (stile Habita79)

- Fissa in alto e **staccata dai bordi** (margine sopra e ai lati, angoli arrotondati), alta 64 px, larga al massimo 1240 px. Vetro rosso con sfocatura di ciò che sta sotto (`backdrop-filter: blur()`): rosso al 78% sopra la foto dell'hero, al 94% sulle pagine con fondo crema, così il testo crema resta sopra 4,5:1 e il rosso non diventa rosa.
- Tre zone in una griglia `1fr auto 1fr`, così il logo resta al centro esatto:
  - a sinistra "SMASHBROSKI / POMPEI" in maiuscolo spaziato, solo decorativo (`aria-hidden`);
  - al centro il logo piccolo, link alla home;
  - a destra l'**ora di Pompei** con sole o luna e le voci **Menù** e **Orari e contatti**.
- **Da 900 px in su** le voci stanno nella barra. **Sotto i 900 px** le sostituisce un **pulsante a tre linee** (`static/js/navbar.js`): le linee diventano una X e un pannello di vetro scende sotto la barra con le voci una sotto l'altra. Si chiude con Esc (il focus torna sul pulsante), con un clic su una voce o fuori dalla barra, e passando a uno schermo largo.
- **Senza JavaScript** il pulsante e l'ora non compaiono: logo a sinistra e voci compatte nella barra.
- L'ora è quella del locale (fuso delle impostazioni), non quella del visitatore; si aggiorna a ogni minuto. Sole tra alba e tramonto di Pompei, luna dopo il tramonto. Per i lettori di schermo: "Ora a Pompei: 21:35".
- La voce della pagina aperta ha `aria-current="page"` ed è sottolineata, non solo colorata.
- I titoli raggiunti con i link interni (`#burger`, `#orari`) non finiscono sotto la navbar fissa (`scroll-padding-top`).
- Con "riduci movimento" le animazioni del pulsante e del pannello sono spente.

### Footer in due fasce (stile Habita79)

1. **Fascia "Dove siamo"** nel blu del logo: etichetta "Dove siamo", indirizzo grande e pulsante **[Come arrivare]** verso Google Maps (RF-06). In fondo alla home il velo dell'hero sfuma nello stesso blu, senza stacco.
2. **Footer rosso**: logo e "Hamburgeria a Pompei"; colonne **Il locale** ([Menù], [Orari e contatti]), **Seguici** ([Facebook], [Instagram]) e **Informazioni** ([Privacy e cookie]); una riga finale con "© anno SmashBroski Pompei" e, solo nella home, il credito della foto (AU-NAV12, RF-08).

- Nelle pagine senza dati del locale (pagine di errore, login e area proprietario) la fascia "Dove siamo" e la colonna Seguici non compaiono.
- Su telefono le colonne vanno a capo; da 768 px sono affiancate a destra del logo.
- Nuove pagine (es. "La nostra storia") si aggiungono come voce della colonna "Il locale".
- Nessun link visibile all'area riservata: il proprietario apre direttamente `/auth/login`.

### Sfondo di loghi (Menù e Orari e contatti)

- Come i vasi del pannello di Habita79: piccoli loghi (il personaggio, senza scritta) in due tinte tenui, in file che scorrono in orizzontale, a file alterne in direzioni opposte. Solo CSS, mattonella WebP di circa 5 KB.
- Il contenuto sta su un **pannello crema pieno** con angoli arrotondati: i loghi non passano mai sotto testi e prezzi.
- Fermo con "riduci movimento"; nascosto ai lettori di schermo (`aria-hidden`).

## Home – mobile (360×800)

```
┌────────────────────────────────────┐
│ ┌────────────────────────────────┐ │
│ │SMASHBROSKI  [logo]     ☀ 21:35 ≡│ │ ← navbar staccata, vetro rosso 78%
│ │POMPEI                          │ │   (≡ = pulsante a tre linee)
│ └────────────────────────────────┘ │
│                                    │
│        (foto del locale, a         │
│         tutto schermo, con         │
│         velo scuro dal basso)      │
│                                    │
│          ┌──────────────┐          │
│          │  LOGO GRANDE │          │ ← dentro l'H1 (alt "SmashBroski")
│          └──────────────┘          │
│        Hamburgeria a Pompei        │ ← resto dell'H1
│                                    │
│   ● Aperto · chiude alle 01:00     │ ← stato apertura (RF-03)
│                                    │
│      [ Guarda il menù ]            │ ← pulsante principale → /menu
│      [ Come arrivare ]             │ ← Google Maps (RF-06)
│                                    │
└────────────────────────────────────┘ ← fine hero (min-height: 100dvh),
│ DOVE SIAMO                         │   il velo sfuma nel blu
│ Vico dei Paninari, 7 -             │ ← fascia blu del logo
│ 80045 Pompei (NA)                  │
│ [ COME ARRIVARE ]                  │
├────────────────────────────────────┤
│ [logo]                             │ ← footer rosso
│ Hamburgeria a Pompei               │
│ IL LOCALE        SEGUICI           │
│ [Menù]           [Facebook]        │
│ [Orari e         [Instagram]       │
│  contatti]                         │
│ INFORMAZIONI                       │
│ [Privacy e cookie]                 │
│ ────────────────────────────────── │
│ © 2026 SmashBroski Pompei          │
│ Foto di lavoro: …, Pexels          │
└────────────────────────────────────┘

Pulsante aperto (sotto i 900 px):
│ ┌────────────────────────────────┐ │
│ │SMASHBROSKI  [logo]     ☀ 21:35 X│ │
│ └────────────────────────────────┘ │
│ ┌────────────────────────────────┐ │
│ │ Menù                           │ │ ← pannello di vetro rosso,
│ │ Orari e contatti               │ │   voci una dopo l'altra
│ └────────────────────────────────┘ │
```

Note:

- **Solo l'hero**: orari e contatti stanno nella pagina `/info`; lo stato di apertura resta nell'hero perché è l'informazione più cercata.
- **Hero**: `min-height: 100dvh`, non `height: 100vh`. Se lo schermo è basso (375×667, 390×600, orizzontale 667×375, zoom al 200%) l'hero si allunga invece di far uscire il contenuto; nessun blocco in `position: absolute` sopra l'hero (AU-UI01, AU-UI02, AU-UI05, AU-UI06, RNF-01).
- **Logo grande**: altezza limitata in base allo schermo, così in orizzontale non spinge fuori pulsanti e stato di apertura.
- **Foto**: elemento `<picture>` con il taglio verticale per i telefoni e quelli orizzontali per gli schermi larghi; `object-fit: cover`. Caricamento immediato (mai `lazy`), perché è l'elemento LCP (RNF-04).
- **Stato di apertura**: testo completo, non solo un pallino colorato ("Aperto · chiude alle 01:00", "Chiuso · apre mercoledì alle 12:00").
- Sotto i 380 px ora e pulsante sono più piccoli, per tenere il logo al centro.

## Home – desktop (1366×768)

```
┌──────────────────────────────────────────────────────────────────────┐
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ SMASHBROSKI            [logo]        ☀ 21:35  Menù  Orari e    │  │ ← navbar staccata
│  │ POMPEI                                              contatti   │  │
│  └────────────────────────────────────────────────────────────────┘  │
│  ┌────────────┐                                                      │
│  │ LOGO GRANDE│           (foto del locale a tutta larghezza,        │
│  └────────────┘            velo scuro da sinistra verso destra:      │
│  Hamburgeria a Pompei      la foto resta visibile a destra)          │
│  ● Aperto · chiude alle 01:00                                        │
│  [ Guarda il menù ]  [ Come arrivare ]                               │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
│  DOVE SIAMO                                                          │ ← fascia blu
│  Vico dei Paninari, 7 - 80045 Pompei (NA)          [ COME ARRIVARE ] │
├──────────────────────────────────────────────────────────────────────┤
│  [logo]                    IL LOCALE      SEGUICI     INFORMAZIONI   │ ← footer rosso
│  Hamburgeria a Pompei      [Menù]         [Facebook]  [Privacy e     │
│                            [Orari e       [Instagram]  cookie]       │
│                             contatti]                                │
│  ──────────────────────────────────────────────────────────────────  │
│  © 2026 SmashBroski Pompei                    Foto di lavoro: …      │
└──────────────────────────────────────────────────────────────────────┘
```

Note:

- Contenuto dell'hero allineato a sinistra, dove il velo è più scuro.
- Footer e fascia con larghezza massima del contenuto di circa 1100 px.

## Menù – mobile (360×800)

```
┌────────────────────────────────────┐
│ ┌────────────────────────────────┐ │
│ │SMASHBROSKI  [logo]     ☀ 21:35 ≡│ │ ← navbar, vetro rosso 94%;
│ │                                │ │   "Menù" con aria-current
│ └────────────────────────────────┘ │
│  (sfondo di loghi in movimento)    │
│ ┌────────────────────────────────┐ │ ← pannello crema
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
└────────────────────────────────────┘ ← fine del pannello
│ fascia "Dove siamo" + footer rosso │
└────────────────────────────────────┘
```

Note:

- Il menù è una sola pagina scritta dal server; l'indice usa link interni e funziona senza JavaScript (RNF-05, RNF-08).
- Il contenuto sta sul pannello crema sopra lo sfondo di loghi (sezione "Elementi comuni").
- Struttura per i lettori di schermo (RF-14, AU-NAV05): `h1` della pagina, `h2` per categoria, `h3` per voce; i prezzi di una voce sono una lista di coppie formato–prezzo (`<dl>`), così il lettore dice "Panino single, 7,00 euro" invece di una serie di numeri.
- Nomi in maiuscolo solo con il CSS: nell'HTML restano "Smash Burger", così la ricerca (Ctrl+F) e la copia funzionano (RF-13).
- Testo dei prezzi almeno grande quanto il testo normale (16 px), leggibile senza zoom a 360 px (RF-10, AU-NAV02).
- Voce con più prezzi su due righe da due (Burger e Menù delle Originals, Single e Menù delle Salad) quando lo spazio basta; altrimenti un prezzo per riga.

## Menù – desktop (1366×768)

```
┌──────────────────────────────────────────────────────────────────────┐
│  │ SMASHBROSKI POMPEI     [logo]     ☀ 21:35  Menù  Orari e contatti│ │ ← "Menù" con aria-current
├──────────────────────────────────────────────────────────────────────┤
│  (sfondo di loghi ai lati del pannello crema centrale)               │
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
├──────────────────────────────────────────────────────────────────────┤
│ fascia "Dove siamo" + footer rosso, come nella home                  │
└──────────────────────────────────────────────────────────────────────┘
```

Note:

- Colonna centrale larga al massimo circa 900 px, per non avere righe troppo lunghe.
- Nelle categorie con formati (Burger, The Originals, Salad, Straccetti) i prezzi si allineano in colonne con l'intestazione "a cascata" del PDF: prima Panino e Menù, sotto single e double. L'intestazione è solo visiva (`aria-hidden`): ogni prezzo ha comunque il suo formato nell'HTML, come su mobile. Un formato mancante (Los Pollos double) è una cella con "—".
- Le categorie brevi senza formati (Soft Drinks e Beers) possono stare affiancate in due colonne.

## Orari e contatti – mobile (360×800)

```
┌────────────────────────────────────┐
│ ┌────────────────────────────────┐ │
│ │SMASHBROSKI  [logo]     ☀ 21:35 ≡│ │ ← "Orari e contatti" con aria-current
│ └────────────────────────────────┘ │
│  (sfondo di loghi in movimento)    │
│ ┌────────────────────────────────┐ │ ← pannello crema
│ │ H1: Orari e contatti           │ │
│ │ ● Aperto · chiude alle 01:00   │ │ ← stato apertura (RF-03)
│ │                                │ │
│ │ H2: Orari                      │ │ ← #orari (RF-02)
│ │ Lunedì    12:00–15:00 ·        │ │
│ │           18:00–01:00          │ │ ← un turno non va a capo
│ │ Martedì   Chiuso               │ │   sul trattino
│ │ Mercoledì (oggi) 12:00–15:00 · │ │ ← oggi: evidenziato,
│ │           18:00–01:00          │ │   grassetto + "(oggi)"
│ │ ...                            │ │
│ │ Domenica  18:00–02:00          │ │
│ │                                │ │
│ │ H2: Contatti                   │ │ ← #contatti
│ │ Telefono: [+39 081 000 0000]   │ │ ← tel: (RF-04)
│ │ (numero di prova)              │ │
│ │ Email: [info@example.com]      │ │ ← mailto: (RF-05)
│ │ Indirizzo: Vico dei Paninari,  │ │
│ │ 7 - 80045 Pompei (NA)          │ │
│ │ [Apri in Google Maps]          │ │ ← RF-06
│ │ [Facebook] [Instagram]         │ │ ← RF-07, area di tocco 44×44
│ └────────────────────────────────┘ │
│ fascia "Dove siamo" + footer rosso │
└────────────────────────────────────┘
```

## Orari e contatti – desktop (1366×768)

```
┌──────────────────────────────────────────────────────────────────────┐
│  │ SMASHBROSKI POMPEI     [logo]     ☀ 21:35  Menù  Orari e contatti│ │
├──────────────────────────────────────────────────────────────────────┤
│  (sfondo di loghi)  ┌──────────────────────────────────┐             │
│                     │ H1: Orari e contatti             │             │
│                     │ ● Aperto · chiude alle 01:00     │             │
│                     │ H2: Orari         H2: Contatti   │             │
│                     │ Lunedì 12:00–…    Telefono …     │             │
│                     │ Martedì Chiuso    Email …        │             │
│                     │ ...               Indirizzo …    │             │
│                     │                   [Maps]         │             │
│                     │                   [Facebook] …   │             │
│                     └──────────────────────────────────┘             │
├──────────────────────────────────────────────────────────────────────┤
│ fascia "Dove siamo" + footer rosso, come nella home                  │
└──────────────────────────────────────────────────────────────────────┘
```

Note:

- Da 768 px Orari e Contatti in due colonne affiancate; sotto, uno sotto l'altro.
- Oggi negli orari: evidenziato, in grassetto e con "(oggi)", non solo il colore. Un turno oltre la mezzanotte resta nel giorno in cui inizia (sezione 3 di `PROGETTAZIONE.md`).
- Il JSON-LD `Restaurant` resta nella home.

## Pagine non disegnate

- **Privacy e cookie** (`/privacy`): navbar, titolo, testo, fascia "Dove siamo" e footer, senza sfondo di loghi. Il testo lo forniscono i titolari; finché manca c'è un testo segnaposto marcato come tale.
- **Login** e **area proprietario**: moduli semplici, senza hero, con il solo footer rosso.
- **Pagine di errore** (404, 500): navbar (ora compresa), messaggio senza dettagli tecnici, solo footer rosso.
