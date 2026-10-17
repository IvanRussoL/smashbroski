# Piano di test – SmashBroski Pompei

Test funzionali manuali e test unitari con pytest del nuovo sito (Flask + MySQL).

| Versione | 1.0 |
|---|---|
| Data | 16 ottobre 2026 |
| Riferimenti | `PROGETTAZIONE.md` (requisiti RF/RNF, regole di business, sicurezza), `WIREFRAME.md`, `Audit_SmashBroski_Fase0.xlsx` (casi AU-xx del sito attuale) |

Il piano ripete sul nuovo sito i casi dell'audit della Fase 0: i FAIL e i BLOCKED devono diventare PASS, i PASS devono restare tali. A questi si aggiungono i casi dell'area proprietario e della sicurezza, che il sito attuale non ha.

Ogni caso indica il **traguardo** per cui serve (sezione 1 di `PROGETTAZIONE.md`):

- **Demo**: si esegue sul prototipo in locale, con i segnaposto.
- **Pubblicazione**: si esegue solo sull'hosting, con dati e foto reali.
- **Demo + Pubblicazione**: si esegue per la demo e si ripete sull'hosting.

## 1. Introduzione e ambiente di test

### 1.1 URL dell'applicazione

- Sviluppo: **http://127.0.0.1:5000**. Nei casi di test i percorsi relativi (es. `/menu`) si intendono relativi a questo indirizzo.
- Pubblicazione: indirizzo dell'hosting, da definire.
- Per i casi su smartphone reale il prototipo deve essere raggiungibile dal telefono nella stessa rete Wi-Fi (indirizzo IP del PC al posto di `127.0.0.1`).

### 1.2 Database e dati

- **Test manuali**: database di sviluppo ricreato con `database/schema.sql` e `database/dati_iniziali.sql` all'inizio di ogni sessione. I casi TC-P modificano i dati: ognuno indica come ripristinarli, oppure si ricarica il database a fine sessione.
- **pytest**: database di prova separato, ricreato dalle fixture in `tests/conftest.py`; non tocca mai il database di sviluppo.
- Valori di riferimento: i dati iniziali della sezione 4 di `PROGETTAZIONE.md` (7 categorie, 10 formati, 25 voci, orari settimanali).

### 1.3 Account di test

- Proprietario di test creato con `flask crea-proprietario`, email `proprietario@example.com`. La password (almeno 12 caratteri) si sceglie al momento e non si scrive in questo documento né nel repository.
- Per il caso dell'account disattivato si usa il client MySQL: `UPDATE utenti SET attivo = 0 WHERE email = 'proprietario@example.com';` e poi `attivo = 1` per ripristinare.

### 1.4 Browser, strumenti e viewport

- Chrome (DevTools: device toolbar, Network, Console, Issues, Lighthouse, Coverage) e Firefox. Finestra in incognito per tutti i casi su cookie e prestazioni.
- Smartphone reale: Oppo Reno 12 Pro (Android) con Chrome e TalkBack. Safari iOS non è disponibile e non viene verificato.
- Lettore di schermo su desktop: NVDA (Windows).
- `curl` per le richieste senza browser (CSRF, header).

Matrice dei viewport, la stessa dell'audit più i casi bassi e in orizzontale:

| Profilo | Viewport (px) | Uso |
|---|---|---|
| Android piccolo | 360×800 | Riferimento mobile del wireframe |
| iPhone SE | 375×667 | Schermo basso |
| Smartphone con barre di sistema | 390×666 e 390×600 | Schermo basso reale |
| iPhone 12–14 | 390×844 | iPhone standard |
| Android grande | 412×915 | Pixel / Galaxy recenti |
| Orizzontale | 667×375 e 844×390 | Telefono ruotato |
| Tablet | 768×1024 | Passaggio da una a due colonne |
| Desktop | 1366×768 | Riferimento desktop del wireframe |
| Zoom 200% | 1366×768 al 200% (equivale a 683×384) | WCAG 1.4.4 |

### 1.5 Ora e stato "aperto ora"

Lo stato di apertura dipende dall'ora. I casi limite (oltre la mezzanotte, inizio incluso e fine esclusa, cambio dell'ora legale) si verificano **solo con pytest**, passando l'istante a `stato_apertura(adesso)` (sezione 3.1). A mano si verifica che lo stato mostrato sia coerente con l'ora reale di Roma; gli altri stati si ottengono cambiando gli orari dall'area proprietario (TC-H02). Il sito non ha un'ora simulata.

### 1.6 Segnaposto

Nella demo telefono, email e social sono segnaposto (sezione 3 di `PROGETTAZIONE.md`). I casi della demo verificano che siano **marcati** come tali; TC-H08 verifica la loro sostituzione per la pubblicazione.

## 2. Casi di test manuali

### Elenco dei casi

| ID | Titolo | Traguardo |
|---|---|---|
| TC-UI01 | Home su smartphone di altezza normale | Demo |
| TC-UI02 | Home su schermi bassi | Demo |
| TC-UI03 | Home e menù in orizzontale | Demo |
| TC-UI04 | Zoom al 200% | Demo |
| TC-UI05 | Assenza di scroll orizzontale | Demo |
| TC-UI06 | Navigazione da tastiera | Demo |
| TC-UI07 | Hero con barra degli indirizzi dinamica (smartphone reale) | Demo + Pubblicazione |
| TC-UI08 | Navbar e impaginazione desktop | Demo |
| TC-H01 | Orari della settimana | Demo |
| TC-H02 | Stato "aperto ora" | Demo |
| TC-H03 | Link del telefono | Demo + Pubblicazione |
| TC-H04 | Link dell'email con e senza JavaScript | Demo |
| TC-H05 | Indirizzo e Google Maps | Demo + Pubblicazione |
| TC-H06 | Link ai social | Demo + Pubblicazione |
| TC-H07 | Footer, pagina Privacy e nessun link all'area riservata | Demo |
| TC-H08 | Dati reali al posto dei segnaposto | Pubblicazione |
| TC-M01 | Apertura del menù e ritorno alla home | Demo |
| TC-M02 | Leggibilità del menù a 360 px senza zoom | Demo |
| TC-M03 | Categorie e indice | Demo |
| TC-M04 | Voci e prezzi uguali ai dati iniziali | Demo |
| TC-M05 | Ricerca nel menù (Ctrl+F) | Demo |
| TC-M06 | Copia di voce e prezzi | Demo |
| TC-M07 | Menù con lettore di schermo | Demo |
| TC-M08 | Etichette di edizione e note | Demo |
| TC-M09 | Menù con JavaScript disattivato | Demo |
| TC-P01 | Login con credenziali valide | Demo |
| TC-P02 | Login con credenziali errate | Demo |
| TC-P03 | Logout | Demo |
| TC-P04 | Account disattivato | Demo |
| TC-P05 | Nuova voce | Demo |
| TC-P06 | Modifica di una voce | Demo |
| TC-P07 | Nascondere e rimostrare una voce | Demo |
| TC-P08 | Validazione dei dati di una voce | Demo |
| TC-P09 | Formato di prezzo di un'altra categoria (manomissione) | Demo |
| TC-P10 | Modifica degli orari | Demo |
| TC-P11 | Orari non validi | Demo |
| TC-S01 | Rotte riservate senza login | Demo |
| TC-S02 | POST senza token CSRF | Demo |
| TC-S03 | Limite di tentativi di login | Demo |
| TC-S04 | Header di sicurezza | Demo + Pubblicazione |
| TC-S05 | Cookie | Demo + Pubblicazione |
| TC-S06 | Testo HTML inserito dal proprietario | Demo |
| TC-S07 | Nessuna risorsa esterna né analisi del traffico | Demo |
| TC-S08 | Pagine di errore e nessuna registrazione pubblica | Demo + Pubblicazione |
| TC-S09 | HTTPS e redirect | Pubblicazione |
| TC-NS01 | Caricamento della home e del menù | Demo + Pubblicazione |
| TC-NS02 | Immagini: formato, peso e dimensioni | Demo + Pubblicazione |
| TC-NS03 | Lighthouse mobile | Demo + Pubblicazione |
| TC-NS04 | Codice CSS e JavaScript non utilizzato | Demo |
| TC-NS05 | Console e pannello Issues | Demo |
| TC-NS06 | Titolo, descrizione e intestazioni | Demo |
| TC-NS07 | Menù nel sorgente e nessuna versione esposta | Demo |
| TC-NS08 | Dati strutturati Restaurant | Demo + Pubblicazione |

### TC-UI — Layout e mobile

#### TC-UI01 — Home su smartphone di altezza normale

| | |
|---|---|
| **Origine** | AU-UI02 · RF-01, RNF-01 |
| **Traguardo** | Demo |
| **Precondizione** | DevTools in modalità device toolbar. Home `/` aperta. |
| **Passi** | 1) Impostare 360×800 e ricaricare.<br>2) Scorrere tutta la pagina e catturare uno screenshot dell'hero e della sezione Contatti.<br>3) In Elements misurare il box dei link Facebook e Instagram.<br>4) Ripetere a 390×844 e 412×915. |
| **Atteso** | Logo, H1, stato di apertura, pulsanti "Guarda il menù" e "Come arrivare" interamente visibili nell'hero. Orari e Contatti sotto l'hero, nessun elemento coperto da un altro. Area di tocco dei link social di almeno 44×44 px. |

#### TC-UI02 — Home su schermi bassi

| | |
|---|---|
| **Origine** | AU-UI01, AU-UI02 · RF-01, RNF-01 |
| **Traguardo** | Demo |
| **Precondizione** | Come TC-UI01. |
| **Passi** | 1) Impostare 375×667 e ricaricare.<br>2) Scorrere tutta la pagina e catturare uno screenshot dell'hero e delle icone social.<br>3) In Elements controllare `position` e `height` dell'hero e del blocco che lo segue.<br>4) Ripetere a 390×666 e 390×600. |
| **Atteso** | Nessun elemento coperto: l'hero si allunga invece di tagliare il contenuto. L'hero usa `min-height: 100dvh`, non `height: 100vh`. Nessun blocco in `position: absolute` sopra l'hero. Icone social intere. |

#### TC-UI03 — Home e menù in orizzontale

| | |
|---|---|
| **Origine** | AU-UI05 · RF-01, RNF-01 |
| **Traguardo** | Demo |
| **Precondizione** | Come TC-UI01. |
| **Passi** | 1) Impostare 844×390 e aprire `/`.<br>2) Scorrere la pagina e catturare uno screenshot dell'hero.<br>3) Ripetere a 667×375.<br>4) Aprire `/menu` agli stessi viewport e scorrere fino in fondo. |
| **Atteso** | Il logo grande non spinge fuori stato di apertura e pulsanti; niente sovrapposizioni con la navbar fissa. Il menù è leggibile e completo. |

#### TC-UI04 — Zoom al 200%

| | |
|---|---|
| **Origine** | AU-UI06 · RF-01, RNF-01 |
| **Traguardo** | Demo |
| **Precondizione** | Chrome desktop, finestra 1366×768. |
| **Passi** | 1) Aprire `/` e impostare lo zoom al 200% (Ctrl +).<br>2) Scorrere tutta la pagina.<br>3) Ripetere su `/menu`.<br>4) Ripristinare lo zoom (Ctrl 0). |
| **Atteso** | Testo e link leggibili, nessuna perdita di contenuto né sovrapposizione. Il logo non è coperto. Nessuno scroll orizzontale. |

#### TC-UI05 — Assenza di scroll orizzontale

| | |
|---|---|
| **Origine** | AU-UI03 · RNF-02 |
| **Traguardo** | Demo |
| **Precondizione** | DevTools in modalità device toolbar, Console aperta. |
| **Passi** | 1) Per ogni viewport della sezione 1.4 aprire `/`, `/menu`, `/privacy` e `/auth/login`.<br>2) In Console eseguire `document.documentElement.scrollWidth > document.documentElement.clientWidth`. |
| **Atteso** | Risultato `false` per ogni pagina e viewport. |

#### TC-UI06 — Navigazione da tastiera

| | |
|---|---|
| **Origine** | AU-UI07 · RNF-02 |
| **Traguardo** | Demo |
| **Precondizione** | Chrome desktop 1366×768, `/` aperta, nessun clic sulla pagina. |
| **Passi** | 1) Premere ripetutamente Tab fino al footer e annotare l'ordine del focus.<br>2) Con il focus su "Orari" nella navbar premere Invio.<br>3) Aprire `/menu`, raggiungere con Tab il link "Burger" dell'indice e premere Invio. |
| **Atteso** | Ordine logico: logo e link della navbar, pulsanti dell'hero, link dei contatti, social, footer. Focus sempre visibile. Dopo Invio il titolo raggiunto ("Orari", "Burger") è visibile e non finisce sotto la navbar fissa. |

#### TC-UI07 — Hero con barra degli indirizzi dinamica (smartphone reale)

| | |
|---|---|
| **Origine** | AU-UI04 (BLOCKED nell'audit) · RNF-01 |
| **Traguardo** | Demo + Pubblicazione |
| **Precondizione** | Oppo Reno 12 Pro con Chrome. Prototipo raggiungibile dal telefono (sezione 1.1). |
| **Passi** | 1) Aprire la home con la barra degli indirizzi visibile e fare uno screenshot.<br>2) Scorrere in basso finché la barra si nasconde e fare uno screenshot.<br>3) Tornare in cima e ruotare il telefono in orizzontale. |
| **Atteso** | Nessun contenuto tagliato in entrambi gli stati della barra né in orizzontale. Pulsanti dell'hero raggiungibili. Nessun salto del layout quando la barra compare o scompare. |

#### TC-UI08 — Navbar e impaginazione desktop

| | |
|---|---|
| **Origine** | — · `WIREFRAME.md` (navbar, home desktop) |
| **Traguardo** | Demo |
| **Precondizione** | Chrome desktop con DevTools. |
| **Passi** | 1) A 360×800 controllare che i tre link della navbar stiano in una riga.<br>2) Su `/` e `/menu` scorrere in modo che sotto la navbar passino la zona più chiara e la più scura della foto e del contenuto; misurare il contrasto del testo della navbar (DevTools, selettore colore).<br>3) Su `/menu` controllare in Elements il link "Menù" della navbar.<br>4) A 1366×768 e a 768×1024 osservare Orari e Contatti. |
| **Atteso** | Link della navbar su una sola riga, senza menù a scomparsa. Contrasto del testo almeno 4,5:1 in tutti i punti. Il link della pagina aperta ha `aria-current="page"` ed è sottolineato. A 1366 px Orari e Contatti sono in due colonne affiancate; sotto i 768 px uno sotto l'altro. |

### TC-H — Home

#### TC-H01 — Orari della settimana

| | |
|---|---|
| **Origine** | AU-NAV11 · RF-02 |
| **Traguardo** | Demo |
| **Precondizione** | Database con gli orari iniziali. |
| **Passi** | 1) Aprire `/` e andare alla sezione Orari.<br>2) Confrontare ogni giorno con la tabella degli orari della sezione 4 di `PROGETTAZIONE.md`.<br>3) Individuare il giorno di oggi. |
| **Atteso** | 7 giorni da lunedì a domenica. "Martedì: Chiuso" scritto per esteso. Turni nel formato "12:00–15:00 · 18:00–01:00"; sabato e domenica "18:00–02:00", nel giorno in cui iniziano. Il giorno di oggi è in grassetto con la parola "oggi". |

#### TC-H02 — Stato "aperto ora"

| | |
|---|---|
| **Origine** | AU-NAV11 · RF-03, RF-19 |
| **Traguardo** | Demo |
| **Precondizione** | Database con gli orari iniziali. Proprietario di test esistente. |
| **Passi** | 1) Annotare giorno e ora attuali di Roma e ricavare dagli orari lo stato atteso.<br>2) Aprire `/` e leggere lo stato nell'hero.<br>3) Dall'area proprietario rendere il giorno di oggi chiuso (o, se oggi è martedì, aggiungere un turno che comprende l'ora attuale); ricaricare `/`.<br>4) Dall'area proprietario togliere tutti i turni della settimana; ricaricare `/`.<br>5) Ripristinare gli orari iniziali. |
| **Atteso** | Passo 2: stato coerente con l'ora reale, scritto per intero ("Aperto · chiude alle 01:00" oppure "Chiuso · apre mercoledì alle 12:00"), non solo un pallino colorato. Passo 3: stato opposto, con l'orario corretto. Passo 4: "orari non disponibili". |
| **Nota** | *I casi limite (mezzanotte, inizio e fine del turno, ora legale) sono coperti da pytest, sezione 3.1.* |

#### TC-H03 — Link del telefono

| | |
|---|---|
| **Origine** | AU-NAV08 (BLOCKED), AU-CON02 · RF-04 |
| **Traguardo** | Demo + Pubblicazione |
| **Precondizione** | Home aperta su desktop; smartphone reale per il passo 3. |
| **Passi** | 1) In Elements leggere l'`href` del telefono.<br>2) Cercare `wa.me` e `whatsapp` nel sorgente (Ctrl+U).<br>3) Su smartphone reale toccare il numero. |
| **Atteso** | `href="tel:+390810000000"`; accanto al numero la scritta "numero di prova". Nessun link WhatsApp. Sul telefono si apre il compositore con il numero già scritto, senza chiamare. Per la pubblicazione: numero reale, senza la scritta. |

#### TC-H04 — Link dell'email con e senza JavaScript

| | |
|---|---|
| **Origine** | AU-NAV09 (PASS, da mantenere) · RF-05 |
| **Traguardo** | Demo |
| **Precondizione** | Chrome desktop. |
| **Passi** | 1) Fare clic sull'email e annotare cosa si apre.<br>2) Disattivare JavaScript (DevTools → Ctrl+Shift+P → "Disable JavaScript") e ricaricare.<br>3) Leggere l'`href` dell'email nel sorgente (Ctrl+U). |
| **Atteso** | `href="mailto:info@example.com"` scritto in chiaro nell'HTML; il link funziona anche senza JavaScript. |

#### TC-H05 — Indirizzo e Google Maps

| | |
|---|---|
| **Origine** | AU-NAV10 (BLOCKED) · RF-06 |
| **Traguardo** | Demo + Pubblicazione |
| **Precondizione** | Home aperta su desktop; smartphone reale per il passo 3. |
| **Passi** | 1) Leggere l'`href` del pulsante "Come arrivare" e del link "Apri in Google Maps".<br>2) Fare clic su entrambi da desktop.<br>3) Toccarli su smartphone reale. |
| **Atteso** | Link a Google Maps costruito dall'indirizzo "Vico dei Paninari, 7 - 80045 Pompei (NA)", non un link breve `maps.app.goo.gl`. Google Maps (sito o app) si apre sulla posizione del locale. |

#### TC-H06 — Link ai social

| | |
|---|---|
| **Origine** | AU-NAV07 · RF-07 |
| **Traguardo** | Demo + Pubblicazione |
| **Precondizione** | Home aperta. |
| **Passi** | 1) Leggere l'`href` dei link Facebook e Instagram.<br>2) Controllare che ogni icona abbia anche il testo visibile.<br>3) Solo per la pubblicazione: aprire i due link senza essere loggati a Facebook o Instagram. |
| **Atteso** | Demo: `https://example.com/facebook-segnaposto` e `https://example.com/instagram-segnaposto`. Nessun link di condivisione temporaneo (`/share/`). Pubblicazione: si aprono le pagine corrette di SmashBroski Pompei anche senza login. |

#### TC-H07 — Footer, pagina Privacy e nessun link all'area riservata

| | |
|---|---|
| **Origine** | AU-NAV12 · RF-08, regola "nessun link visibile all'area riservata" |
| **Traguardo** | Demo |
| **Precondizione** | Nessun login. |
| **Passi** | 1) Aprire `/`, `/menu`, `/privacy` e `/auth/login` e scorrere fino in fondo.<br>2) Fare clic su "Privacy e cookie".<br>3) Cercare nel sorgente di `/` e `/menu` i testi `auth`, `login` e `proprietario`. |
| **Atteso** | Su ogni pagina un footer con nome del locale, indirizzo e link "Privacy e cookie". La pagina Privacy si apre; finché mancano i testi dei titolari mostra un testo segnaposto marcato come tale. Nessun link all'area riservata nelle pagine pubbliche. |

#### TC-H08 — Dati reali al posto dei segnaposto

| | |
|---|---|
| **Origine** | — · Sezione 1 di `PROGETTAZIONE.md` ("pronto per la pubblicazione") |
| **Traguardo** | Pubblicazione |
| **Precondizione** | Dati reali forniti dai titolari e caricati; sito sull'hosting. |
| **Passi** | 1) Cercare nel sorgente di ogni pagina `example.com`, `numero di prova`, `081 000 0000` e la parola "segnaposto".<br>2) Controllare la foto dell'hero e `docs/CREDITI_IMMAGINI.md`.<br>3) Leggere la pagina `/privacy`. |
| **Atteso** | Nessun segnaposto. Foto vera del locale nell'hero. Testo della privacy fornito dai titolari. Crediti delle immagini aggiornati. |

### TC-M — Menù

#### TC-M01 — Apertura del menù e ritorno alla home

| | |
|---|---|
| **Origine** | AU-NAV01 · RF-09 |
| **Traguardo** | Demo |
| **Precondizione** | Home aperta, su desktop e a 360×800. |
| **Passi** | 1) Fare clic su "Guarda il menù".<br>2) Premere il tasto Indietro.<br>3) Fare clic su "Menù" nella navbar, poi sul logo. |
| **Atteso** | Il menù si apre nella stessa scheda all'indirizzo `/menu`, come pagina HTML (nessun PDF, nessun `target="_blank"`). Indietro e il logo riportano alla home. |

#### TC-M02 — Leggibilità del menù a 360 px senza zoom

| | |
|---|---|
| **Origine** | AU-NAV02 · RF-10 |
| **Traguardo** | Demo |
| **Precondizione** | `/menu` aperto a 360×800, zoom 100%. Per il passo 3 smartphone reale. |
| **Passi** | 1) Senza zoom, leggere nome, ingredienti e i 4 prezzi dello Smash Cheeseburger.<br>2) In Elements leggere il `font-size` calcolato del testo e dei prezzi.<br>3) Ripetere il passo 1 su smartphone reale e contare i gesti di zoom necessari. |
| **Atteso** | Tutto leggibile con 0 gesti di zoom. `font-size` di testo e prezzi di almeno 16 px. |

#### TC-M03 — Categorie e indice

| | |
|---|---|
| **Origine** | AU-NAV02, AU-NAV06 · RF-11 |
| **Traguardo** | Demo |
| **Precondizione** | `/menu` aperto a 360×800 e a 1366×768. |
| **Passi** | 1) Leggere i titoli delle categorie dall'alto in basso.<br>2) Fare clic su ogni link dell'indice.<br>3) Dalla fine di una categoria fare clic su "Torna all'indice". |
| **Atteso** | 7 categorie nell'ordine: Starters, Salad, Burger, Kids Menù, Soft Drinks, Beers, The Originals. Ogni link porta alla sua categoria (`/menu#burger` ecc.) e il titolo resta visibile sotto la navbar. "Torna all'indice" riporta all'indice. |

#### TC-M04 — Voci e prezzi uguali ai dati iniziali

| | |
|---|---|
| **Origine** | AU-NAV04, AU-NAV06 · RF-12 |
| **Traguardo** | Demo |
| **Precondizione** | Database con i dati iniziali. `/menu` aperto a 360×800 e a 1366×768. |
| **Passi** | 1) Contare le voci per categoria.<br>2) Per ogni voce confrontare nome, descrizione e prezzi con la sezione 4 di `PROGETTAZIONE.md`.<br>3) Controllare le voci Los Pollos Classic e Los Pollos Bacon a entrambi i viewport. |
| **Atteso** | 25 voci (3, 2, 7, 2, 3, 3, 5), tutte uguali ai dati iniziali. Ogni prezzo ha il formato scritto accanto (es. "Panino single 7,00 €") e il formato italiano "7,00 €". Mobile: per Los Pollos solo i formati esistenti, senza righe vuote. Desktop: prezzi in colonne con l'intestazione a cascata; per i double di Los Pollos la cella mostra "—". |

#### TC-M05 — Ricerca nel menù (Ctrl+F)

| | |
|---|---|
| **Origine** | AU-NAV03 · RF-13 |
| **Traguardo** | Demo |
| **Precondizione** | `/menu` aperto su Chrome desktop. |
| **Passi** | 1) Premere Ctrl+F.<br>2) Cercare in sequenza: SALAD, DRINKS, Cheeseburger, Pollos.<br>3) Annotare il numero di risultati. |
| **Atteso** | Ogni parola trovata almeno una volta. DRINKS trova "Soft Drinks" (nel sito attuale: 0 risultati). |

#### TC-M06 — Copia di voce e prezzi

| | |
|---|---|
| **Origine** | AU-NAV04 · RF-13 |
| **Traguardo** | Demo |
| **Precondizione** | `/menu` aperto a 360×800 e a 1366×768. Editor di testo aperto. |
| **Passi** | 1) Selezionare con il mouse la voce Smash Cheeseburger con i suoi prezzi.<br>2) Copiare (Ctrl+C) e incollare nell'editor.<br>3) Ripetere all'altro viewport. |
| **Atteso** | Il testo incollato contiene, nell'ordine: "Smash Cheeseburger" (non tutto maiuscolo), "Hamburger, cheddar, salsa smash", "Panino single 7,00 €", "Panino double 8,50 €", "Menù single 11,00 €", "Menù double 12,00 €". Nessun prezzo di altre voci. |

#### TC-M07 — Menù con lettore di schermo

| | |
|---|---|
| **Origine** | AU-NAV05 · RF-14 |
| **Traguardo** | Demo |
| **Precondizione** | NVDA su desktop; TalkBack su smartphone reale. |
| **Passi** | 1) Aprire `/menu` e scorrere i titoli (NVDA: tasto H).<br>2) Far leggere la categoria The Originals.<br>3) Annotare l'ordine in cui vengono letti nomi, ingredienti e prezzi.<br>4) Ripetere i passi 2-3 con TalkBack. |
| **Atteso** | Un titolo di livello 1 ("Menù"), un titolo di livello 2 per categoria, un titolo di livello 3 per voce. Ogni voce è letta insieme ai suoi ingredienti e prezzi, con il formato prima del prezzo ("Burger, 9,00 euro"). L'intestazione a colonne del desktop non viene letta. |

#### TC-M08 — Etichette di edizione e note

| | |
|---|---|
| **Origine** | AU-NAV06 (in parte) · RF-15 |
| **Traguardo** | Demo |
| **Precondizione** | `/menu` aperto. |
| **Passi** | 1) Controllare le voci di The Originals.<br>2) Leggere le note sotto i titoli delle categorie Burger e The Originals.<br>3) Leggere la voce Veggy 2.0. |
| **Atteso** | "Winter Edition" su Scarulella Bro e Friariello Bro; "Summer Edition" su Fungitiello e Scapece, come semplice testo. Nota di Burger ("Brooo, prova il menù…") e di The Originals ("Ortaggio su base stagionale"). Nota di Veggy 2.0: "Prova anche la variante con la zucca". |

#### TC-M09 — Menù con JavaScript disattivato

| | |
|---|---|
| **Origine** | — · RNF-05, RNF-08 |
| **Traguardo** | Demo |
| **Precondizione** | Chrome desktop, JavaScript disattivato (DevTools → "Disable JavaScript"). |
| **Passi** | 1) Aprire `/menu`.<br>2) Usare l'indice e "Torna all'indice". |
| **Atteso** | Menù completo e indice funzionante, come con JavaScript attivo. |

### TC-P — Area proprietario

#### TC-P01 — Login con credenziali valide

| | |
|---|---|
| **Origine** | — · RF-16, sezione 7 (sessione) |
| **Traguardo** | Demo |
| **Precondizione** | Proprietario di test attivo. Finestra in incognito. |
| **Passi** | 1) Aprire `/auth/login`.<br>2) Inserire email e password corrette e fare clic su "Accedi".<br>3) In DevTools → Application → Cookies leggere gli attributi del cookie di sessione. |
| **Atteso** | Redirect a `/proprietario/` con l'elenco delle voci per categoria. Cookie di sessione con `HttpOnly` e `SameSite=Lax`, durata massima 8 ore. |

#### TC-P02 — Login con credenziali errate

| | |
|---|---|
| **Origine** | — · RF-16, sezione 7 (messaggio generico) |
| **Traguardo** | Demo |
| **Precondizione** | Nessun login. |
| **Passi** | 1) Inserire l'email corretta e una password errata.<br>2) Inserire un'email non registrata (es. `nessuno@example.com`) e una password qualsiasi.<br>3) Inviare il modulo con i campi vuoti. |
| **Atteso** | Nei passi 1 e 2 lo stesso messaggio "email o password non corretti", nessun redirect. Passo 3: messaggio di campo obbligatorio. In nessun caso si capisce se l'email è registrata. |

#### TC-P03 — Logout

| | |
|---|---|
| **Origine** | — · RF-16 |
| **Traguardo** | Demo |
| **Precondizione** | Proprietario autenticato. |
| **Passi** | 1) Fare clic su "Esci".<br>2) Aprire `/proprietario/`.<br>3) Aprire nella barra degli indirizzi `/auth/logout` (richiesta GET). |
| **Atteso** | Passo 1: sessione svuotata, redirect alla home o al login. Passo 2: redirect a `/auth/login`. Passo 3: risposta 405, il logout funziona solo con POST. |

#### TC-P04 — Account disattivato

| | |
|---|---|
| **Origine** | — · Sezione 7 ("utente ricaricato a ogni richiesta") |
| **Traguardo** | Demo |
| **Precondizione** | Proprietario autenticato. Client MySQL aperto. |
| **Passi** | 1) Disattivare l'account con la query della sezione 1.3.<br>2) Ricaricare `/proprietario/`.<br>3) Riprovare il login con le credenziali corrette.<br>4) Riattivare l'account. |
| **Atteso** | Passo 2: redirect a `/auth/login`, accesso perso subito. Passo 3: messaggio generico "email o password non corretti". |

#### TC-P05 — Nuova voce

| | |
|---|---|
| **Origine** | AU-NAV01-06 · RF-17, RF-19 |
| **Traguardo** | Demo |
| **Precondizione** | Proprietario autenticato. Database con i dati iniziali. |
| **Passi** | 1) Aprire `/proprietario/voci/nuova`.<br>2) Creare in Burger la voce "Test Burger", descrizione "Voce di prova", posizione 8, prezzi Panino single `7,5` e Menù single `10,50`.<br>3) Creare in Soft Drinks la voce "Test Drink" con prezzo unico 1,50.<br>4) Aprire `/menu` in un'altra scheda. |
| **Atteso** | Entrambe le voci salvate con un messaggio di conferma. In `/menu` compaiono subito: "Test Burger" in fondo a Burger con i due prezzi e i loro formati ("Panino single 7,50 €", "Menù single 10,50 €"), "Test Drink" in Soft Drinks con "1,50 €". |
| **Ripristino** | Nascondere le due voci (TC-P07) o ricaricare il database. |

#### TC-P06 — Modifica di una voce

| | |
|---|---|
| **Origine** | AU-NAV01-06 · RF-17, RF-19 |
| **Traguardo** | Demo |
| **Precondizione** | Proprietario autenticato. Database con i dati iniziali. |
| **Passi** | 1) Aprire la voce Smash Burger.<br>2) Cambiare il prezzo Panino single da 7,00 a 7,50, togliere il prezzo Menù double e spostarla in posizione 3.<br>3) Salvare e aprire `/menu`. |
| **Atteso** | In `/menu` Smash Burger è terza in Burger, con Panino single 7,50 € e senza Menù double. Le altre voci sono invariate. |
| **Ripristino** | Rimettere i valori iniziali o ricaricare il database. |

#### TC-P07 — Nascondere e rimostrare una voce

| | |
|---|---|
| **Origine** | — · RF-17, RF-19, regola "una voce non si cancella ma si nasconde" |
| **Traguardo** | Demo |
| **Precondizione** | Proprietario autenticato. |
| **Passi** | 1) Nell'elenco nascondere la voce Scarulella Bro.<br>2) Aprire `/menu`, cercarla con Ctrl+F e nel sorgente (Ctrl+U).<br>3) Tornare all'elenco e rimostrarla.<br>4) Riaprire `/menu`.<br>5) Nascondere entrambe le voci del Kids Menù e riaprire `/menu`.<br>6) Rimostrare una delle due e riaprire `/menu`; poi rimostrare anche l'altra. |
| **Atteso** | Passo 2: la voce non c'è né nella pagina né nel sorgente. Nell'elenco del proprietario resta visibile, marcata come nascosta. Passo 4: la voce torna nella stessa posizione con gli stessi dati, prezzi ed edizione. Passo 5: il titolo "Kids Menù" e il suo link nell'indice non ci sono più; nell'area proprietario la categoria resta elencata. Passo 6: categoria e link tornano al loro posto con la sola voce visibile. |

#### TC-P08 — Validazione dei dati di una voce

| | |
|---|---|
| **Origine** | — · Sezione 3 (regole dei prezzi), sezione 7 (validazione sul server) |
| **Traguardo** | Demo |
| **Precondizione** | Proprietario autenticato. Modulo "nuova voce" aperto, categoria Burger. |
| **Passi** | Salvare ogni volta una voce valida tranne per il dato indicato:<br>1) prezzo `0`;<br>2) prezzo `1000`;<br>3) prezzo `7,505`;<br>4) prezzo `7.50` (con il punto);<br>5) prezzo `abc`;<br>6) nessun prezzo;<br>7) un prezzo unico e un prezzo Panino single insieme;<br>8) nome vuoto;<br>9) nome di 101 caratteri;<br>10) nome "Smash Burger" (già presente in Burger). |
| **Atteso** | Per ogni passo: modulo mostrato di nuovo con i dati inseriti e un messaggio sul campo sbagliato, codice 400, nessuna voce salvata (controllare `/menu`). Nessun errore 500. |

#### TC-P09 — Formato di prezzo di un'altra categoria (manomissione)

| | |
|---|---|
| **Origine** | — · Sezione 3 ("il server rifiuta un formato di un'altra categoria") |
| **Traguardo** | Demo |
| **Precondizione** | Proprietario autenticato. Modulo di modifica della voce Smash Burger aperto. |
| **Passi** | 1) In DevTools → Elements cambiare l'identificativo del formato di un prezzo con quello di un formato di Salad (es. "Single").<br>2) Salvare.<br>3) Ripetere togliendo dal modulo gli attributi `required` e `pattern` e inviando un prezzo vuoto. |
| **Atteso** | Salvataggio rifiutato con messaggio e codice 400; la voce resta invariata. La validazione avviene sul server, non solo nel modulo HTML. |

#### TC-P10 — Modifica degli orari

| | |
|---|---|
| **Origine** | AU-NAV11 · RF-18, RF-19 |
| **Traguardo** | Demo |
| **Precondizione** | Proprietario autenticato. Database con gli orari iniziali. |
| **Passi** | 1) Aprire `/proprietario/orari`.<br>2) Rendere chiuso il mercoledì.<br>3) Cambiare il secondo turno del venerdì in 18:00–02:00.<br>4) Salvare e aprire `/`. |
| **Atteso** | In home: "Mercoledì: Chiuso" e "Venerdì 12:00–15:00 · 18:00–02:00", con il turno oltre la mezzanotte nel giorno in cui inizia. Lo stato "aperto ora" tiene conto dei nuovi orari. |
| **Ripristino** | Rimettere gli orari iniziali o ricaricare il database. |

#### TC-P11 — Orari non validi

| | |
|---|---|
| **Origine** | — · Sezione 3 (turni non sovrapposti, verifica sul server) |
| **Traguardo** | Demo |
| **Precondizione** | Proprietario autenticato. `/proprietario/orari` aperto con gli orari iniziali. |
| **Passi** | Salvare ogni volta una sola modifica:<br>1) lunedì 12:00–15:00 e 14:00–16:00;<br>2) lunedì con un turno 01:00–03:00 (la domenica resta 18:00–02:00);<br>3) un turno 12:00–12:00;<br>4) un turno 25:00–26:00, inviato dopo aver tolto i controlli del modulo da DevTools. |
| **Atteso** | Ogni salvataggio è rifiutato con un messaggio che indica il problema, codice 400. Gli orari salvati restano quelli iniziali. |

### TC-S — Sicurezza

#### TC-S01 — Rotte riservate senza login

| | |
|---|---|
| **Origine** | — · Sezione 6 (Blueprint `proprietario`), sezione 7 |
| **Traguardo** | Demo |
| **Precondizione** | Nessun login. Finestra in incognito. |
| **Passi** | Aprire direttamente: `/proprietario/`, `/proprietario/voci/nuova`, `/proprietario/voci/1`, `/proprietario/orari`. |
| **Atteso** | Ogni volta redirect a `/auth/login`. Nessun dato dell'area riservata nella risposta. |
| **Nota** | *La verifica su tutte le rotte registrate, comprese quelle future, la fa pytest (sezione 3.6).* |

#### TC-S02 — POST senza token CSRF

| | |
|---|---|
| **Origine** | — · Sezione 7 (CSRF) |
| **Traguardo** | Demo |
| **Precondizione** | Proprietario autenticato in Chrome; cookie di sessione copiato da DevTools. |
| **Passi** | 1) `curl -i -X POST http://127.0.0.1:5000/auth/logout`<br>2) `curl -i -X POST -b "session=<cookie>" http://127.0.0.1:5000/proprietario/voci/1/visibilita`<br>3) Ripetere il passo 2 con un token `csrf_token` alterato di un carattere. |
| **Atteso** | Risposta 400 in tutti i casi. La voce 1 resta visibile e la sessione resta valida. |

#### TC-S03 — Limite di tentativi di login

| | |
|---|---|
| **Origine** | — · Sezione 7 (Flask-Limiter) |
| **Traguardo** | Demo |
| **Precondizione** | Nessun login. |
| **Passi** | 1) Sbagliare la password 6 volte entro un minuto.<br>2) Attendere un minuto e accedere con le credenziali corrette. |
| **Atteso** | I primi 5 tentativi mostrano il messaggio generico; il sesto riceve la risposta 429. Dopo un minuto il login funziona. |

#### TC-S04 — Header di sicurezza

| | |
|---|---|
| **Origine** | AU-NET07 · RNF-06 |
| **Traguardo** | Demo + Pubblicazione |
| **Precondizione** | DevTools → Network. |
| **Passi** | 1) Aprire `/`, `/menu`, `/auth/login` e, da autenticato, `/proprietario/`.<br>2) Per ognuna leggere Response Headers del documento HTML. |
| **Atteso** | Su tutte: `Content-Security-Policy` con il valore della sezione 7 di `PROGETTAZIONE.md`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`. Su `/proprietario/` anche `Cache-Control: no-store`. In sviluppo nessun `Strict-Transport-Security`; in pubblicazione `Strict-Transport-Security: max-age=31536000`. |

#### TC-S05 — Cookie

| | |
|---|---|
| **Origine** | AU-NAV12 · RNF-11, sezione 7 |
| **Traguardo** | Demo + Pubblicazione |
| **Precondizione** | Finestra in incognito appena aperta. |
| **Passi** | 1) Aprire `/`, `/menu` e `/privacy`; in DevTools → Application → Cookies annotare i cookie.<br>2) Aprire `/auth/login` e annotare i cookie. |
| **Atteso** | Passo 1: nessun cookie. Passo 2: solo il cookie di sessione, con `HttpOnly` e `SameSite=Lax`; in pubblicazione anche `Secure`. Nessun banner cookie necessario, perché ci sono solo cookie tecnici. |

#### TC-S06 — Testo HTML inserito dal proprietario

| | |
|---|---|
| **Origine** | — · Sezione 7 (XSS) |
| **Traguardo** | Demo |
| **Precondizione** | Proprietario autenticato. |
| **Passi** | 1) Creare in Beers una voce con nome `<b>Prova</b>` e descrizione `<i>corsivo</i>`, prezzo 1,00.<br>2) Aprire `/menu` e l'elenco del proprietario.<br>3) Nascondere la voce. |
| **Atteso** | Nome e descrizione mostrati come testo, con i simboli `<` e `>` visibili, non in grassetto né in corsivo. Nel sorgente compaiono come `&lt;b&gt;`. |

#### TC-S07 — Nessuna risorsa esterna né analisi del traffico

| | |
|---|---|
| **Origine** | AU-NAV12 · RNF-11, sezione 7 |
| **Traguardo** | Demo |
| **Precondizione** | DevTools → Network, Preserve log attivo, Disable cache attivo. |
| **Passi** | 1) Aprire `/` e `/menu`.<br>2) Ordinare le richieste per dominio. |
| **Atteso** | Tutte le richieste vanno al sito stesso. Nessuna richiesta a `googletagmanager.com`, `google-analytics.com`, font o script esterni. |

#### TC-S08 — Pagine di errore e nessuna registrazione pubblica

| | |
|---|---|
| **Origine** | — · Sezione 3 (accessi), sezione 7 (debug) |
| **Traguardo** | Demo + Pubblicazione |
| **Precondizione** | Nessun login. |
| **Passi** | 1) Aprire `/pagina-inesistente`.<br>2) Aprire `/auth/register` e `/registrazione`.<br>3) Da autenticato, aprire `/proprietario/voci/99999`. |
| **Atteso** | Pagina 404 del sito, con navbar e footer, senza dettagli tecnici. Nessuna pagina di registrazione. In pubblicazione nessuna pagina di debug di Flask in nessun caso. |

#### TC-S09 — HTTPS e redirect

| | |
|---|---|
| **Origine** | AU-NET06 (PASS, da mantenere) |
| **Traguardo** | Pubblicazione |
| **Precondizione** | Sito sull'hosting. DevTools → Network con Preserve log attivo. |
| **Passi** | 1) Digitare l'indirizzo del sito con `http://`.<br>2) Annotare la catena di redirect e i codici di stato. |
| **Atteso** | Un solo redirect 301 verso HTTPS, poi 200. Nessun 4xx/5xx, nessun contenuto misto. |

### TC-NS — Rete, prestazioni e SEO

#### TC-NS01 — Caricamento della home e del menù

| | |
|---|---|
| **Origine** | AU-NET01 (PASS, da mantenere), AU-NET03 (confronto con il PDF) |
| **Traguardo** | Demo + Pubblicazione |
| **Precondizione** | Finestra in incognito. DevTools → Network: Disable cache, throttling "Regular 4G", viewport 390×844. |
| **Passi** | 1) Aprire `/` e annotare richieste, dati trasferiti, DOMContentLoaded e Load.<br>2) Ripetere su `/menu`. |
| **Atteso** | Per ogni pagina meno di 1 MB trasferito e Load sotto i 3 s. Valori annotati per il confronto con il sito attuale (18 richieste, 378 KB, Load 1,60 s) e con il PDF del menù (127 KB). |

#### TC-NS02 — Immagini: formato, peso e dimensioni

| | |
|---|---|
| **Origine** | AU-NET02 · RNF-03, RNF-04 |
| **Traguardo** | Demo + Pubblicazione |
| **Precondizione** | Come TC-NS01, filtro "Img". |
| **Passi** | 1) Aprire `/` e annotare formato, peso e dimensioni di logo e foto dell'hero.<br>2) In Elements leggere gli attributi `<img>` e `<picture>`. |
| **Atteso** | Logo in WebP sotto i 200 KB con `width` e `height` nell'HTML. Foto dell'hero in WebP, con il taglio verticale a 390 px e quello orizzontale a 1366 px, senza `loading="lazy"`. |

#### TC-NS03 — Lighthouse mobile

| | |
|---|---|
| **Origine** | AU-NET04 (PASS, da mantenere) · RNF-04 |
| **Traguardo** | Demo + Pubblicazione |
| **Precondizione** | Finestra in incognito senza estensioni. Lighthouse: Navigation, Mobile, tutte le categorie. |
| **Passi** | 1) Eseguire l'analisi di `/` 3 volte.<br>2) Per **ogni** esecuzione registrare i punteggi delle 4 categorie e LCP, CLS e TBT.<br>3) Calcolare la mediana.<br>4) Ripetere su `/menu`. |
| **Atteso** | Mediana di LCP ≤ 2,5 s e di CLS ≤ 0,1 su entrambe le pagine. Tutte le metriche registrate per tutte e 3 le esecuzioni (nell'audit mancano quelle delle Run 1 e 2). Per la pubblicazione si ripete sull'hosting con la foto vera. |

#### TC-NS04 — Codice CSS e JavaScript non utilizzato

| | |
|---|---|
| **Origine** | AU-NET05 · RNF-05 |
| **Traguardo** | Demo |
| **Precondizione** | Chrome desktop 1366×768, DevTools aperto. |
| **Passi** | 1) Ctrl+Shift+P → "Show Coverage".<br>2) Ricaricare dal pannello Coverage `/` e poi `/menu`.<br>3) Annotare file, peso e percentuale non utilizzata. |
| **Atteso** | Un solo foglio di stile del sito, nessun framework CSS né file del page builder. Percentuale di codice non utilizzato annotata e inferiore a quella del sito attuale (57%, 450 KB su 779 KB). |

#### TC-NS05 — Console e pannello Issues

| | |
|---|---|
| **Origine** | AU-CON01 (PASS, da mantenere), AU-CON02 |
| **Traguardo** | Demo |
| **Precondizione** | Finestra in incognito. Console su "All levels", Preserve log attivo. |
| **Passi** | 1) Aprire `/`, `/menu`, `/privacy`, `/auth/login` e, da autenticato, `/proprietario/` e `/proprietario/orari`.<br>2) Annotare errori e avvisi in Console.<br>3) Aprire DevTools → More tools → Issues e annotare le segnalazioni. |
| **Atteso** | Nessun errore in Console (comprese violazioni della CSP e risorse 404). Nessuna segnalazione nel pannello Issues. |

#### TC-NS06 — Titolo, descrizione e intestazioni

| | |
|---|---|
| **Origine** | AU-SEO01 · RNF-07 |
| **Traguardo** | Demo |
| **Precondizione** | Sorgente delle pagine pubbliche (Ctrl+U). |
| **Passi** | Per `/`, `/menu` e `/privacy`:<br>1) annotare `<title>`;<br>2) cercare `meta name="description"`;<br>3) contare gli `<h1>`. |
| **Atteso** | `<title>` con tipo di locale e città, es. "SmashBroski Pompei – Hamburgeria a Pompei" per la home. Meta description presente e diversa per ogni pagina. Un solo `<h1>` per pagina. |

#### TC-NS07 — Menù nel sorgente e nessuna versione esposta

| | |
|---|---|
| **Origine** | AU-SEO02, AU-SEO03 · RNF-08, RNF-09 |
| **Traguardo** | Demo |
| **Precondizione** | Sorgente di `/menu` e `/` (Ctrl+U), cioè l'HTML inviato dal server. |
| **Passi** | 1) Nel sorgente di `/menu` cercare "Cheeseburger" e "Los Pollos".<br>2) Nel sorgente di `/` e `/menu` cercare "generator". |
| **Atteso** | "Cheeseburger" e "Los Pollos" presenti come testo nell'HTML. Nessun meta `generator` né altra versione del software. |

#### TC-NS08 — Dati strutturati Restaurant

| | |
|---|---|
| **Origine** | AU-SEO04 · RNF-10 |
| **Traguardo** | Demo + Pubblicazione |
| **Precondizione** | Sorgente di `/` (Ctrl+U). |
| **Passi** | 1) Cercare `application/ld+json` e copiare il contenuto.<br>2) Incollarlo nel validatore di Schema.org (validator.schema.org, scheda "Snippet di codice").<br>3) Solo per la pubblicazione: analizzare l'indirizzo pubblico con il Test dei risultati avanzati di Google. |
| **Atteso** | Un oggetto `@type: Restaurant` con nome, indirizzo, orari di apertura uguali al calendario e link a `/menu`. Nessun errore nel validatore. Demo: nessun telefono, perché è un numero di prova. Pubblicazione: telefono reale presente. |

## 3. Test unitari (pytest)

I test si trovano in `tests/` e si eseguono con `pytest` dalla cartella del progetto. Le fixture di `tests/conftest.py` creano un'app con `create_app()` e la configurazione di test, un database di prova con i dati iniziali, un client di test e un proprietario di test. Nei test CSRF e rate limiting sono disattivati, tranne nei test che li verificano (sezione 3.6).

I servizi si testano senza Flask; le rotte con il client di test di Flask.

### 3.1 OrariService — stato di apertura

File: `tests/test_orari_service.py`

Calendario: orari iniziali della sezione 4 di `PROGETTAZIONE.md`. Gli istanti sono nel fuso Europe/Rome; le date fanno riferimento a ottobre 2026 (lunedì 19, martedì 20, mercoledì 21, sabato 24, domenica 25).

| Test | Scenario |
|---|---|
| test_lunedi_1200_aperto_inizio_incluso | Lunedì 12:00 → aperto, chiude alle 15:00 |
| test_lunedi_1459_aperto | Lunedì 14:59 → aperto |
| test_lunedi_1500_chiuso_fine_esclusa | Lunedì 15:00 → chiuso, prossima apertura lunedì 18:00 |
| test_martedi_0030_aperto_per_turno_di_lunedi | Martedì 00:30 → aperto (turno di lunedì 18:00–01:00), chiude alle 01:00 |
| test_martedi_0100_chiuso | Martedì 01:00 → chiuso, prossima apertura mercoledì 12:00 |
| test_martedi_1000_chiuso_apre_mercoledi | Martedì 10:00 → chiuso, prossima apertura mercoledì 12:00 |
| test_lunedi_0130_aperto_per_turno_di_domenica | Lunedì 01:30 → aperto (turno di domenica 18:00–02:00) |
| test_sabato_1000_apre_stesso_giorno | Sabato 10:00 → chiuso, prossima apertura sabato 18:00 |
| test_domenica_0159_aperto_domenica_0200_chiuso | Domenica 01:59 → aperto (turno di sabato); 02:00 → chiuso |
| test_cambio_ora_solare_ora_ripetuta | Domenica 25/10/2026, 02:30 nella prima e nella seconda occorrenza (ritorno all'ora solare) → chiuso |
| test_calendario_vuoto_nessuna_apertura | Nessun turno → chiuso, nessuna prossima apertura ("orari non disponibili") |
| test_un_solo_turno_prossima_apertura_dopo_7_giorni | Solo lunedì 12:00–15:00; lunedì 16:00 → prossima apertura il lunedì successivo alle 12:00 |

### 3.2 OrariService e Turno — validazione del calendario

File: `tests/test_orari_service.py`, `tests/test_modelli.py`

| Test | Scenario |
|---|---|
| test_turno_supera_mezzanotte | 18:00–01:00 → sì; 12:00–15:00 → no |
| test_turno_intervallo_finisce_giorno_dopo | 18:00–01:00 del 19/10 → inizio 19/10 18:00, fine 20/10 01:00 |
| test_calendario_iniziale_valido | Gli orari dei dati iniziali si salvano senza errori |
| test_turni_stesso_giorno_sovrapposti_errore | Lunedì 12:00–15:00 e 14:00–16:00 → `DatiNonValidiError` |
| test_turni_adiacenti_accettati | Lunedì 12:00–15:00 e 15:00–18:00 → accettati (fine esclusa) |
| test_turno_oltre_mezzanotte_sovrapposto_giorno_dopo_errore | Domenica 18:00–02:00 e lunedì 01:00–03:00 → `DatiNonValidiError` |
| test_turno_oltre_mezzanotte_adiacente_giorno_dopo_accettato | Domenica 18:00–02:00 e lunedì 02:00–04:00 → accettati |
| test_inizio_uguale_fine_errore | 12:00–12:00 → `DatiNonValidiError` |
| test_ora_formato_non_valido_errore | "25:00", "12.30", "" → `DatiNonValidiError` |
| test_giorno_fuori_intervallo_errore | Giorno 0 e giorno 8 → `DatiNonValidiError` |
| test_salvataggio_rifiutato_non_modifica_orari | Dopo un errore gli orari nel database sono quelli di prima |

### 3.3 MenuService — prezzi e voci

File: `tests/test_menu_service.py`

| Test | Scenario |
|---|---|
| test_converti_prezzo_validi | "7" → 700; "7,5" → 750; "7,50" → 750; "0,01" → 1; "999,99" → 99999 |
| test_converti_prezzo_non_validi | "0", "0,00", "1000", "-1", "7,505", "7.50", "abc", "" → `DatiNonValidiError` |
| test_menu_pubblico_categorie_in_ordine | 7 categorie nell'ordine del PDF |
| test_menu_pubblico_25_voci_in_ordine_di_posizione | 25 voci, ognuna nella sua categoria e in ordine di posizione |
| test_menu_pubblico_esclude_voci_nascoste | Una voce nascosta non compare |
| test_menu_pubblico_esclude_categorie_senza_voci_visibili | Tutte le voci del Kids Menù nascoste → la categoria non c'è; una voce rimostrata → la categoria torna |
| test_menu_pubblico_query_costanti | Il numero di query non cresce con il numero di voci (nessuna query per voce) |
| test_crea_voce_prezzo_unico | Soft Drinks, prezzo unico 1,50 → salvata |
| test_crea_voce_con_formati | Burger, Panino single 7,50 e Menù single 10,50 → salvata con 2 prezzi |
| test_crea_voce_prezzo_unico_in_categoria_con_formati | Starters, prezzo unico 3,50 → salvata (come Patatine stick) |
| test_prezzo_unico_e_formati_insieme_errore | Prezzo unico più Panino single → `DatiNonValidiError` |
| test_formato_di_altra_categoria_errore | Voce Burger con il formato "Single" di Salad → `DatiNonValidiError` |
| test_formato_in_categoria_senza_formati_errore | Voce Beers con un formato qualsiasi → `DatiNonValidiError` |
| test_formato_ripetuto_errore | Due prezzi Panino single → `DatiNonValidiError` |
| test_voce_senza_prezzi_errore | Nessun prezzo → `DatiNonValidiError` |
| test_lunghezze_massime | Nome vuoto o di 101 caratteri, descrizione di 256 → `DatiNonValidiError` |
| test_nome_duplicato_nella_categoria_errore | "Smash Burger" in Burger → `DatiNonValidiError`, non un errore del database |
| test_errore_nessun_salvataggio_parziale | Voce con un prezzo non valido: nessuna riga in `voci_menu` né in `prezzi_voce` (transazione annullata) |
| test_modifica_sostituisce_prezzi | Togliere un formato e cambiare un prezzo → nel database solo i prezzi nuovi |
| test_nascondi_e_rimostra | Dopo nascondi e rimostra la voce ha gli stessi dati e prezzi |
| test_voce_inesistente | Modifica della voce 99999 → `NonTrovatoError` |
| test_testo_con_apici_salvato_come_testo | Nome `Bro's '; DROP TABLE voci_menu; --` salvato e riletto uguale; la tabella esiste ancora |

### 3.4 Filtro euro e modelli

File: `tests/test_filtri.py`, `tests/test_modelli.py`

| Test | Scenario |
|---|---|
| test_euro | 700 → "7,00 €"; 750 → "7,50 €"; 1 → "0,01 €"; 99999 → "999,99 €" |
| test_ha_prezzo_unico | Voce con un prezzo senza formato → sì; voce con formati → no |
| test_link_maps | `Impostazioni.link_maps()` → URL di Google Maps con l'indirizzo codificato, non `maps.app.goo.gl` |

### 3.5 AuthService

File: `tests/test_auth_service.py`

| Test | Scenario |
|---|---|
| test_login_corretto | Email e password corrette → restituisce l'utente |
| test_login_password_errata | Password errata → `None` |
| test_login_email_inesistente_verifica_comunque | Email inesistente → `None`; la verifica Argon2 viene eseguita comunque, sull'hash fittizio |
| test_login_account_disattivato | Credenziali corrette, `attivo` = no → `None` |
| test_hash_argon2id | L'hash salvato inizia con `$argon2id$` e non contiene la password |
| test_rehash_parametri_superati | Hash creato con parametri più deboli → dopo il login l'hash nel database è aggiornato |
| test_crea_proprietario_password_corta | Password di 11 caratteri → `DatiNonValidiError` |
| test_crea_proprietario_email_duplicata | Email già registrata → `DatiNonValidiError` |

### 3.6 Rotte, accessi e sicurezza

File: `tests/test_rotte_pubbliche.py`, `tests/test_accessi.py`, `tests/test_header_sicurezza.py`

| Test | Scenario |
|---|---|
| test_home_contenuti | GET `/` → 200; un solo `<h1>`; `<title>` con "Hamburgeria" e "Pompei"; meta description; `tel:+390810000000` con "numero di prova"; `mailto:info@example.com`; link a Google Maps; link a `/privacy`; nessun `wa.me` |
| test_home_nessun_link_area_riservata | Nell'HTML di `/` e `/menu` nessun link a `/auth` o `/proprietario` |
| test_home_stato_apertura | Con l'ora sostituita nel test (monkeypatch): martedì 10:00 → "Chiuso · apre domani alle 12:00" ("oggi" e "domani" quando la riapertura è vicina, altrimenti il nome del giorno) |
| test_home_json_ld | JSON-LD leggibile, `@type` Restaurant, indirizzo, orari, link al menù; nessun `telephone` con `telefono_di_prova` = sì; `telephone` presente con `telefono_di_prova` = no |
| test_json_ld_escape | Nome del locale con `</script>` → il JSON-LD non chiude lo script |
| test_menu_struttura | GET `/menu` → 200; 7 `<h2>` con `id` uguale allo slug, nell'ordine del PDF; 25 `<h3>`; "Smash Cheeseburger" scritto così nell'HTML |
| test_menu_prezzi_e_formati | "Panino single" e "7,00 €" accanto a Smash Burger; Los Pollos senza prezzi double |
| test_menu_voce_nascosta_assente | Voce nascosta assente dall'HTML |
| test_menu_categoria_vuota_assente | Kids Menù con tutte le voci nascoste → nessun `<h2 id="kids-menu">` e nessun link `#kids-menu` nell'indice |
| test_escape_testo_proprietario | Voce con nome `<b>Prova</b>` → nell'HTML `&lt;b&gt;Prova&lt;/b&gt;` |
| test_nessun_generator | Nessun meta `generator` in `/`, `/menu`, `/privacy` |
| test_pagine_pubbliche_senza_cookie | GET `/`, `/menu`, `/privacy` → nessun `Set-Cookie` |
| test_pagina_404 | GET `/pagina-inesistente` → 404 con la pagina del sito |
| test_nessuna_registrazione | GET `/auth/register` → 404 |
| test_rotte_proprietario_anonimo_redirect | Per **ogni** rotta registrata con prefisso `/proprietario` (lette da `app.url_map`): anonimo → redirect a `/auth/login` |
| test_rotte_proprietario_autenticato | Proprietario autenticato → GET `/proprietario/` e `/proprietario/orari` → 200 |
| test_account_disattivato_perde_accesso | Autenticato, poi `attivo` = no → la richiesta successiva va al login |
| test_login_sessione_solo_id | Dopo il login la sessione contiene solo l'`id` dell'utente; i valori messi prima del login sono spariti |
| test_login_messaggio_generico | Password errata ed email inesistente → stesso messaggio e stesso codice |
| test_logout_solo_post | GET `/auth/logout` → 405; POST → sessione svuotata |
| test_csrf_post_senza_token | Con CSRF attivo: POST a `/auth/logout`, `/proprietario/voci/nuova`, `/proprietario/voci/1/visibilita`, `/proprietario/orari` senza token → 400 |
| test_rate_limit_login | Con il limite attivo: il sesto POST a `/auth/login` nello stesso minuto → 429 |
| test_dati_non_validi_400 | POST di una voce con prezzo "abc" → 400 con il messaggio nel modulo |
| test_voce_inesistente_404 | GET `/proprietario/voci/99999` da autenticato → 404 |
| test_header_sicurezza | Su `/`, `/menu`, `/privacy`, `/auth/login` e sulla pagina 404: CSP con il valore della sezione 7, `nosniff`, `DENY`, `strict-origin-when-cross-origin` |
| test_cache_no_store_area_riservata | Pagine `/proprietario` → `Cache-Control: no-store` |
| test_hsts_solo_produzione | Configurazione di test → nessun `Strict-Transport-Security`; configurazione di produzione → `max-age=31536000` |
| test_cookie_sessione_attributi | Cookie di sessione `HttpOnly` e `SameSite=Lax`; con la configurazione di produzione anche `Secure` |

## 4. Matrice di tracciabilità

### 4.1 Casi dell'audit → requisiti → test

| AU | Esito audit | Requisiti | Casi manuali | pytest |
|---|---|---|---|---|
| AU-NET01 | PASS | RNF-04, RNF-05 | TC-NS01 | — |
| AU-NET02 | FAIL | RNF-03 | TC-NS02 | — |
| AU-NET03 | PASS | — | N.A.: il PDF non esiste più; il peso di `/menu` si misura in TC-NS01 | — |
| AU-NET04 | PASS | RNF-04 | TC-NS03 | — |
| AU-NET05 | FAIL | RNF-05 | TC-NS04 | — |
| AU-NET06 | PASS | — (hosting) | TC-S09 | — |
| AU-NET07 | FAIL | RNF-06 | TC-S04 | test_header_sicurezza, test_hsts_solo_produzione |
| AU-CON01 | PASS | — | TC-NS05 | — |
| AU-CON02 | FAIL | RF-04 | TC-NS05, TC-H03 | test_home_contenuti |
| AU-UI01 | FAIL | RF-01, RNF-01 | TC-UI02 | — |
| AU-UI02 | FAIL | RF-01, RNF-01 | TC-UI01, TC-UI02 | — |
| AU-UI03 | PASS | RNF-02 | TC-UI05 | — |
| AU-UI04 | BLOCKED | RNF-01 | TC-UI07 | — |
| AU-UI05 | FAIL | RF-01, RNF-01 | TC-UI03 | — |
| AU-UI06 | FAIL | RF-01, RNF-01 | TC-UI04 | — |
| AU-UI07 | PASS | RNF-02 | TC-UI06 | — |
| AU-NAV01 | FAIL | RF-09 | TC-M01 | — |
| AU-NAV02 | FAIL | RF-10, RF-11 | TC-M02, TC-M03 | test_menu_struttura |
| AU-NAV03 | FAIL | RF-13 | TC-M05 | test_menu_struttura |
| AU-NAV04 | FAIL | RF-12, RF-13 | TC-M04, TC-M06 | test_menu_prezzi_e_formati |
| AU-NAV05 | FAIL | RF-14 | TC-M07 | test_menu_struttura |
| AU-NAV06 | FAIL | RF-11, RF-12, RF-15 | TC-M03, TC-M04, TC-M08 | test_menu_prezzi_e_formati |
| AU-NAV07 | FAIL | RF-07 | TC-H06, TC-H08 | — |
| AU-NAV08 | BLOCKED | RF-04 | TC-H03 | test_home_contenuti |
| AU-NAV09 | PASS | RF-05 | TC-H04 | test_home_contenuti |
| AU-NAV10 | BLOCKED | RF-06 | TC-H05 | test_link_maps |
| AU-NAV11 | FAIL | RF-02, RF-03, RF-18 | TC-H01, TC-H02, TC-P10 | sezioni 3.1 e 3.2, test_home_stato_apertura |
| AU-NAV12 | FAIL | RF-08, RNF-11 | TC-H07, TC-S05, TC-S07 | test_pagine_pubbliche_senza_cookie |
| AU-SEO01 | FAIL | RNF-07 | TC-NS06 | test_home_contenuti |
| AU-SEO02 | FAIL | RNF-08 | TC-NS07 | test_menu_struttura |
| AU-SEO03 | FAIL | RNF-09 | TC-NS07 | test_nessun_generator |
| AU-SEO04 | FAIL | RNF-10 | TC-NS08 | test_home_json_ld |

Parti dell'audit lasciate fuori perimetro (sezione 2 di `PROGETTAZIONE.md`): allergeni e servizi offerti (AU-NAV06, AU-NAV11), WhatsApp (AU-NAV08).

### 4.2 Requisiti senza un caso dell'audit

| Requisito / regola | Casi manuali | pytest |
|---|---|---|
| RF-16 Login e logout | TC-P01, TC-P02, TC-P03 | sezione 3.5, test_login_*, test_logout_solo_post |
| RF-17 Gestione delle voci | TC-P05, TC-P06, TC-P07, TC-P08, TC-P09 | sezione 3.3 |
| RF-18 Gestione degli orari | TC-P10, TC-P11 | sezione 3.2 |
| RF-19 Modifiche visibili subito | TC-P05, TC-P06, TC-P07, TC-P10 | test_menu_voce_nascosta_assente |
| Accessi (sezione 6-7) | TC-S01, TC-P04, TC-S08 | test_rotte_proprietario_*, test_account_disattivato_perde_accesso, test_nessuna_registrazione |
| CSRF, rate limiting, XSS, SQL | TC-S02, TC-S03, TC-S06 | test_csrf_post_senza_token, test_rate_limit_login, test_escape_testo_proprietario, test_testo_con_apici_salvato_come_testo |
| Navbar e impaginazione (`WIREFRAME.md`) | TC-UI08 | — |
| Menù senza JavaScript (RNF-05, RNF-08) | TC-M09 | — |
| Segnaposto sostituiti | TC-H08 | — |

## 5. Note per il tester

- **Ordine di esecuzione**: prima `pytest` (deve passare tutto), poi i casi manuali nell'ordine TC-NS05 → TC-UI → TC-H → TC-M → TC-P → TC-S → TC-NS. TC-NS05 va per primo perché un errore in Console spiega spesso i FAIL successivi.
- **Database**: ricaricare i dati iniziali all'inizio della sessione e dopo i casi TC-P che non vengono ripristinati.
- **Aspetto grafico**: a differenza del piano di riferimento, layout e leggibilità sono **nel perimetro**, perché sono i FAIL principali dell'audit. Colori e font si valutano solo per il contrasto (4,5:1).
- **Dispositivi reali**: i casi si eseguono nel browser emulato e con gli strumenti da riga di comando, tranne quelli che richiedono uno smartphone reale o un lettore di schermo: TC-UI07, il passo 3 di TC-H03 e di TC-H05, il passo 3 di TC-M02, TC-M07 (TalkBack e NVDA). Questi si eseguono sull'Oppo Reno 12 Pro e, per NVDA, sul PC Windows.
- **Casi di sola pubblicazione** (TC-H08, TC-S09 e le parti "Pubblicazione" degli altri) si eseguono solo sull'hosting, dopo aver caricato i dati reali.

## 6. Tracciamento dell'esito

Gli esiti si registrano in un foglio Excel nello stesso formato di `Audit_SmashBroski_Fase0.xlsx`, da creare in Fase 2 fuori dal repository Git. Per ogni caso eseguito:

| Campo | Contenuto |
|---|---|
| ID test | es. TC-M06 |
| Traguardo | Demo / Pubblicazione |
| Esito | PASS / FAIL / BLOCKED / N.A. |
| Data/ora | es. 2026-11-05 14:35 |
| Viewport / dispositivo | es. Chrome DevTools 360×800, Pixel 7 con TalkBack |
| Evidenza | Nome dello screenshot (es. `TC-M06_360x800.png`) o note testuali con l'URL visitato |
| Errori console/network | Messaggi di errore da DevTools (Console o Network) |
| Note | Comportamento inatteso, differenze rispetto all'atteso, causa ipotizzata |

In caso di **FAIL** includere sempre:

- URL esatto e viewport al momento del fallimento;
- messaggio di errore visibile a schermo, o assenza del messaggio atteso;
- eventuali errori in Console o Network (codice di stato, risposta);
- il commit Git su cui è stato eseguito il test.
