# Progettazione – SmashBroski Pompei

## 1. Problema e utenti

**Obiettivo.** Realizzare un prototipo funzionante del nuovo sito di SmashBroski Pompei da presentare ai titolari, e da pubblicare nel portfolio GitHub. Il prototipo usa i dati reali del locale (menù, prezzi, orari, indirizzo) e segnaposto dichiarati per ciò che non abbiamo ancora (telefono, email, social, foto). Deve dimostrare, con i FAIL dell'audit come riferimento, che il nuovo sito risolve i problemi di quello attuale e che il titolare può aggiornare da solo menù e orari. Se la proposta viene accettata, si sostituiscono i segnaposto e si pubblica senza riprogettare.

Il lavoro ha due traguardi:

- **Pronto per la demo**: tutte le funzioni delle sezioni 2-3 funzionano e i test passano; i segnaposto sono ammessi, purché marcati.
- **Pronto per la pubblicazione**: dati e foto reali al posto dei segnaposto, testo della privacy fornito dai titolari, hosting con HTTPS.

Il sito attuale di SmashBroski Pompei (smashbroski.example, WordPress con Oxygen Builder) è una sola pagina con il logo, un pulsante "MENÙ" che apre un PDF, le icone di Facebook e Instagram, telefono, email e indirizzo. L'audit della Fase 0 (`Audit_SmashBroski_Fase0.xlsx`: 32 casi, 21 FAIL, di cui 7 di gravità alta) ha mostrato tre problemi principali:

- su molti smartphone la fascia dei contatti copre le icone social e, in orizzontale o con lo zoom al 200%, anche il logo (AU-UI01, AU-UI02, AU-UI05, AU-UI06);
- il menù esiste solo come PDF di stampa da 85,8×140,5 cm: su telefono non si legge senza zoom, la ricerca e la copia danno risultati sbagliati, i lettori di schermo non lo leggono e i motori di ricerca non vedono i piatti (AU-NAV01-05, AU-SEO02);
- in home mancano gli orari di apertura, il giorno di chiusura e un footer con le informazioni legali (AU-NAV11, AU-NAV12).

La nuova applicazione rifà la stessa pagina in Flask e MySQL, senza aggiungere funzioni: una home leggibile su qualsiasi schermo, il menù come pagina HTML e un'area riservata in cui il proprietario aggiorna da solo voci, prezzi e orari, senza dover rifare il PDF.

Gli utenti sono due:

- **Visitatore**: chi apre il sito, quasi sempre da smartphone, per vedere menù, prezzi e orari o per contattare e raggiungere il locale. Non ha un account.
- **Proprietario**: titolare del locale; accede all'area riservata con email e password per aggiornare il menù e gli orari.

## 2. Requisiti

Ogni requisito indica il caso dell'audit che risolve. "—" indica un requisito nuovo, senza un FAIL corrispondente.

### Visitatore – Home e Orari e contatti

Dal 18/10 (grafica 2) la home è solo l'hero; orari e contatti sono nella pagina **Orari e contatti** (`/info`), raggiungibile dalla navbar e dal footer di ogni pagina (DEVLOG).

| ID | Requisito | Risolve |
|---|---|---|
| RF-01 | La home mostra logo, stato di apertura, pulsante per il menù e "Come arrivare"; la pagina Orari e contatti mostra telefono, email, indirizzo e link Facebook e Instagram; indirizzo e social sono anche nel footer. Tutto visibile e senza sovrapposizioni su qualsiasi dimensione di schermo, in verticale e in orizzontale, e con lo zoom al 200% | AU-UI01, AU-UI02, AU-UI05, AU-UI06 |
| RF-02 | La pagina Orari e contatti mostra gli orari della settimana, con il giorno di oggi evidenziato e con il giorno di chiusura scritto in modo esplicito ("Martedì: chiuso") | AU-NAV11 |
| RF-03 | La home e la pagina Orari e contatti mostrano se il locale è aperto o chiuso in questo momento e, se è chiuso, quando riapre (es. "Chiuso · apre domani alle 12:00"; "oggi" e "domani" quando la riapertura è vicina, altrimenti il nome del giorno, es. "apre venerdì alle 12:00") | AU-NAV11 |
| RF-04 | Il telefono è un link `tel:` che avvia la chiamata; il numero fisso non porta mai a WhatsApp. Dal 22/10 la pagina Orari e contatti ha un pulsante WhatsApp con un numero suo (`whatsapp`, link `wa.me`), segnaposto finché i titolari non lo danno (DEVLOG) | AU-CON02, AU-NAV08 (BLOCKED) |
| RF-05 | L'email è un link `mailto:` scritto in chiaro nell'HTML, che funziona anche senza JavaScript | AU-NAV09 (PASS, da mantenere) |
| RF-06 | L'indirizzo apre Google Maps sulla posizione del locale, con un link costruito dall'indirizzo al posto del link breve attuale | AU-NAV10 (BLOCKED) |
| RF-07 | I link social (per ora testuali) portano agli indirizzi stabili delle pagine Facebook e Instagram del locale, non a link di condivisione temporanei | AU-NAV07 |
| RF-08 | In fondo a ogni pagina c'è un footer con nome del locale e link alle pagine del sito e a "Privacy e cookie"; nelle pagine pubbliche lo precede la fascia "Dove siamo" con indirizzo e link a Google Maps, e il footer ha anche i social | AU-NAV12 |

### Visitatore – Menù

| ID | Requisito | Risolve |
|---|---|---|
| RF-09 | Il menù è una pagina HTML del sito (`/menu`) che si apre nella stessa scheda; si torna alla home con il tasto Indietro o toccando il logo | AU-NAV01 |
| RF-10 | Su uno smartphone largo 360 px nomi, ingredienti e prezzi si leggono senza zoom | AU-NAV02 |
| RF-11 | Le voci sono divise nelle categorie del PDF attuale, nel suo ordine: Starters, Salad, Burger, Kids Menù, Soft Drinks, Beers, The Originals. In cima alla pagina un indice porta direttamente a ogni categoria | AU-NAV02, AU-NAV06 |
| RF-12 | Ogni voce mostra nome, ingredienti (se presenti) e prezzi, ognuno con il proprio formato scritto accanto (es. "Panino single", "Menù double") | AU-NAV04, AU-NAV06 |
| RF-13 | Tutto il menù è testo HTML: si trova con la ricerca del browser (Ctrl+F) e copiando una voce si copiano nome e prezzi nell'ordine giusto | AU-NAV03, AU-NAV04 |
| RF-14 | Il menù è leggibile dai lettori di schermo: ogni categoria è un titolo e ogni voce viene letta insieme ai suoi ingredienti e prezzi | AU-NAV05 |
| RF-15 | Le etichette "Winter Edition" e "Summer Edition" sono riportate come semplice testo, dove compaiono nel PDF | AU-NAV06 (in parte) |

### Proprietario

| ID | Requisito | Risolve |
|---|---|---|
| RF-16 | Accede all'area riservata con email e password ed esce con il logout; dal 24/10 cambia la propria password dall'area (serve quella attuale). Account, password dimenticate e blocchi li gestisce lo sviluppatore da riga di comando (`docs/GESTIONE_SITO.md`) | — |
| RF-17 | Aggiunge, modifica, nasconde e rimostra le voci del menù: nome, ingredienti, prezzi, categoria, posizione nella categoria, etichetta di edizione, nota | AU-NAV01-06 (il menù si aggiorna senza rifare il PDF) |
| RF-18 | Modifica gli orari settimanali: per ogni giorno, chiuso oppure uno o più turni, anche oltre la mezzanotte | AU-NAV11 |
| RF-19 | Le modifiche sono visibili subito nelle pagine pubbliche | — |

### Requisiti non funzionali

| ID | Requisito | Risolve |
|---|---|---|
| RNF-01 | Layout mobile-first in flusso normale: nessun blocco in `position: absolute` sopra un'area alta quanto lo schermo; altezze con `min-height: 100dvh` invece di `height: 100vh`. Verifica a 360×800, 375×667, 390×600, 667×375, 844×390 e a 1366×768 con zoom al 200% | AU-UI01, AU-UI02, AU-UI05, AU-UI06; AU-UI04 (BLOCKED) da verificare su smartphone reale |
| RNF-02 | Nessuno scroll orizzontale; tutti i link raggiungibili da tastiera con focus visibile | AU-UI03, AU-UI07 (PASS, da mantenere) |
| RNF-03 | Logo in formato WebP sotto i 200 KB, con `width` e `height` indicati nell'HTML | AU-NET02 |
| RNF-04 | Lighthouse mobile (mediana di 3 esecuzioni): LCP ≤ 2,5 s e CLS ≤ 0,1 | AU-NET04 (PASS con LCP 2,3 s, da mantenere) |
| RNF-05 | Un solo foglio di stile e poco JavaScript scritti per il sito, senza framework CSS né page builder, così non si carica codice inutilizzato | AU-NET05 |
| RNF-06 | Header di sicurezza su tutte le risposte: Content-Security-Policy, X-Content-Type-Options, X-Frame-Options, Referrer-Policy e, in produzione, Strict-Transport-Security | AU-NET07 |
| RNF-07 | `<title>` con tipo di locale e città (es. "SmashBroski Pompei – Hamburgeria a Pompei"), meta description e un solo `<h1>` per pagina | AU-SEO01 |
| RNF-08 | Il menù è scritto dal server nell'HTML della pagina, quindi è indicizzabile dai motori di ricerca | AU-SEO02 |
| RNF-09 | Nessuna versione del software esposta nelle pagine (nessun meta `generator`) | AU-SEO03 |
| RNF-10 | Dati strutturati JSON-LD di tipo `Restaurant` con nome, indirizzo, orari e link al menù | AU-SEO04 |
| RNF-11 | Nessuno strumento di analisi del traffico e solo cookie tecnici (la sessione dell'area proprietario) | AU-NAV12 |

## 3. Regole di business

### Menù

- Le **categorie sono fisse** in questa fase: le 7 del PDF, caricate con i dati iniziali. Il proprietario gestisce le voci, non le categorie.
- Ogni voce appartiene a **una sola categoria** e ha una **posizione** che ne decide l'ordine dentro la categoria.
- I prezzi sono **interi in centesimi di euro** (750 = 7,50 €), maggiori di 0. Sul sito si mostrano nel formato italiano: "7,50 €".
- I **formati di prezzo** li definisce la categoria, come le colonne del PDF:
  - **Burger**: Panino single hamb., Panino double hamb., Menù single hamb., Menù double hamb. I Los Pollos hanno solo i due prezzi single.
  - **The Originals**: Burger e Menù.
  - **Salad**: Single e Menù.
  - **Starters**: 5 pz e 10 pz (solo per gli Straccetti di pollo).
  - **Kids Menù, Soft Drinks, Beers**: nessun formato.
- Una voce ha **un prezzo unico senza formato** oppure **uno o più prezzi con i formati della sua categoria**, mai le due cose insieme; ogni formato compare al massimo una volta. Il server rifiuta un formato di un'altra categoria.
- Il **nome di una voce è unico nella sua categoria**: il servizio rifiuta un doppione con un messaggio sul campo, prima che intervenga il vincolo univoco del database. In modifica la voce può tenere il proprio nome.
- Il proprietario scrive i prezzi in euro con la **virgola** e al massimo due decimali: "7" vale 7,00 €, "7,5" e "7,50" valgono 7,50 €; il punto ("7.50") è rifiutato, per non confondere decimali e migliaia.
- Una voce non si cancella ma si **nasconde**: non compare nel menù pubblico e si può rimostrare senza riscriverla (utile per le voci stagionali).
- Una **categoria senza voci visibili** non compare nel menù pubblico, né come titolo né nell'indice; ricompare quando il proprietario rimostra almeno una sua voce. Nell'area proprietario resta sempre elencata.
- L'**etichetta di edizione** (es. "Winter Edition") e le **note** di categoria e di voce (es. "Ortaggio su base stagionale") sono testi facoltativi che si mostrano e basta: nessuna logica di stagione in questa fase.
- I prezzi dei dati iniziali si prendono dalla **resa visiva del PDF**, controllati a vista voce per voce, e non dal suo livello di testo, che li assegna alla riga sbagliata (AU-NAV04).

### Orari e "aperto ora"

- Il locale ha un **calendario settimanale**: per ogni giorno nessun turno (chiuso) oppure uno o più turni, con ora di inizio e di fine nell'ora locale.
- Orari di partenza: lunedì 12:00–15:00 e 18:00–01:00; martedì chiuso; mercoledì, giovedì e venerdì 12:00–15:00 e 18:00–01:00; sabato e domenica 18:00–02:00.
- Un turno **appartiene al giorno in cui inizia**. Se l'ora di fine è precedente a quella di inizio, il turno finisce il giorno dopo: lunedì 18:00–01:00 finisce martedì all'01:00. Inizio e fine uguali non sono ammessi.
- Il locale è **aperto** in un istante se l'istante cade in un turno del giorno corrente **oppure** in un turno del giorno precedente che supera la mezzanotte. L'inizio è incluso, la fine esclusa. Esempi:
  - martedì 00:30 → aperto (turno di lunedì, anche se martedì è chiuso);
  - martedì 01:00 → chiuso;
  - lunedì 01:30 → aperto (turno di domenica 18:00–02:00);
  - lunedì 12:00 → aperto; lunedì 15:00 → chiuso.
- La **prossima apertura** è il primo inizio di turno dopo l'istante, cercato nei 7 giorni successivi (es. martedì 10:00 → "apre mercoledì alle 12:00"). Se il calendario non ha turni, home e pagina Orari e contatti mostrano "orari non disponibili".
- I turni non si sovrappongono: né due turni dello stesso giorno, né un turno oltre la mezzanotte con un turno del giorno dopo (es. domenica 18:00–02:00 è incompatibile con un turno di lunedì che inizia prima delle 02:00).
- Le regole sono **verificate dal server** quando il proprietario salva gli orari, non solo dal modulo HTML.
- L'ora attuale si calcola nel fuso **Europe/Rome** (modulo `zoneinfo`), non in quello del server, così il cambio dell'ora legale è gestito.
- Nella pagina Orari e contatti ogni turno si mostra nel giorno in cui inizia: "Lunedì 12:00–15:00 · 18:00–01:00".

### Contatti e dati del locale

- Il progetto è un'iniziativa personale: finché i titolari non forniscono i dati reali, **telefono, email e link social sono segnaposto**, marcati come tali nei dati iniziali e in questo documento.
  - Telefono: `+39 081 000 0000`; sul sito compare con la scritta "numero di prova" e non si inserisce nei dati strutturati JSON-LD.
  - Email: `info@example.com`.
  - Facebook e Instagram: `https://example.com/facebook-segnaposto` e `https://example.com/instagram-segnaposto` (il dominio `example.com` è riservato agli esempi e non porta al sito di nessuno).
- Indirizzo: Vico dei Paninari, 7 - 80045 Pompei (NA), dato pubblico del locale, usato anche per il link a Google Maps.
- Logo: l'attuale `Burger.png`, convertito in WebP senza modificarne il contenuto.
- In questa fase contatti e logo si cambiano solo dai dati iniziali, non dall'area proprietario.

### Accessi

- Solo il proprietario accede all'area riservata; non esiste una registrazione pubblica.
- Il primo proprietario si crea da riga di comando (`flask crea-proprietario`), non da una pagina del sito.
- Le pagine pubbliche sono in sola lettura: i visitatori non inviano moduli.

## 4. Modello dei dati (tabelle e relazioni)

Convenzione: le colonne DATETIME sono in **UTC** (`creato_il` la scrive MySQL con `UTC_TIMESTAMP()`); le colonne TIME degli orari sono nell'**ora locale** del locale (Europe/Rome), come il calendario esposto al pubblico.

### Tabella `utenti`

Contiene gli account dell'area riservata. Esiste un solo ruolo, il proprietario, quindi non serve una colonna `ruolo`.

| Colonna | Tipo | Significato |
|---|---|---|
| `id` | INT, chiave primaria, auto-incrementale | Identificativo numerico univoco |
| `email` | VARCHAR(255), obbligatoria, univoca | Email usata per il login |
| `password_hash` | VARCHAR(255), obbligatoria | Hash Argon2id della password (`argon2-cffi`); la password in chiaro non viene mai salvata |
| `attivo` | BOOLEAN, obbligatoria, predefinito sì | Se vale no l'account non può accedere; si disattiva invece di cancellare |
| `creato_il` | DATETIME, obbligatoria, predefinito data e ora attuali | Momento di creazione, scritto dal database |

### Tabella `categorie`

Contiene le 7 categorie del menù. Sono fisse in questa fase: le crea lo script dei dati iniziali.

| Colonna | Tipo | Significato |
|---|---|---|
| `id` | INT, chiave primaria, auto-incrementale | Identificativo numerico univoco |
| `nome` | VARCHAR(50), obbligatoria, univoca | Nome mostrato (es. "The Originals") |
| `slug` | VARCHAR(50), obbligatoria, univoca | Identificativo per l'indice della pagina (es. `/menu#the-originals`); solo lettere minuscole, cifre e trattini |
| `posizione` | TINYINT, obbligatoria | Ordine della categoria nella pagina, come nel PDF |
| `nota` | VARCHAR(255), facoltativa | Testo mostrato sotto il titolo della categoria (es. "Ortaggio su base stagionale") |

### Tabella `formati_prezzo`

Contiene i formati di prezzo di ogni categoria, cioè le colonne di prezzo del PDF. Una categoria senza righe ha solo prezzi unici.

| Colonna | Tipo | Significato |
|---|---|---|
| `id` | INT, chiave primaria, auto-incrementale | Identificativo numerico univoco |
| `categoria_id` | INT, obbligatoria, chiave esterna verso `categorie.id` | La categoria a cui appartiene il formato |
| `etichetta` | VARCHAR(40), obbligatoria | Testo mostrato accanto al prezzo (es. "Menù double hamb.") |
| `posizione` | TINYINT, obbligatoria | Ordine delle colonne di prezzo |

Vincolo: (`categoria_id`, `etichetta`) univoco.

### Tabella `voci_menu`

Contiene i piatti e le bevande. Li gestisce il proprietario.

| Colonna | Tipo | Significato |
|---|---|---|
| `id` | INT, chiave primaria, auto-incrementale | Identificativo numerico univoco |
| `categoria_id` | INT, obbligatoria, chiave esterna verso `categorie.id` | La categoria della voce |
| `nome` | VARCHAR(100), obbligatoria | Nome della voce, salvato in maiuscolo/minuscolo normale (es. "Smash Burger"); il maiuscolo del PDF lo applica il CSS |
| `descrizione` | VARCHAR(255), facoltativa | Ingredienti o composizione |
| `edizione` | VARCHAR(30), facoltativa | Etichetta come "Winter Edition", solo da mostrare |
| `nota` | VARCHAR(255), facoltativa | Testo aggiuntivo (es. "Prova anche la variante con la zucca") |
| `posizione` | SMALLINT, obbligatoria | Ordine dentro la categoria |
| `attiva` | BOOLEAN, obbligatoria, predefinito sì | Se vale no la voce è nascosta nel menù pubblico |

Vincolo: (`categoria_id`, `nome`) univoco. Indice: (`categoria_id`, `attiva`, `posizione`) per la pagina del menù.

### Tabella `prezzi_voce`

Contiene i prezzi di ogni voce: una riga per prezzo.

| Colonna | Tipo | Significato |
|---|---|---|
| `id` | INT, chiave primaria, auto-incrementale | Identificativo numerico univoco |
| `voce_id` | INT, obbligatoria, chiave esterna verso `voci_menu.id`, `ON DELETE CASCADE` | La voce a cui appartiene il prezzo |
| `formato_id` | INT, facoltativa, chiave esterna verso `formati_prezzo.id` | Il formato del prezzo; vuota se è il prezzo unico della voce |
| `prezzo_centesimi` | INT, obbligatoria, maggiore di 0 (CHECK) | Prezzo in centesimi di euro (850 = 8,50 €) |

Vincolo: (`voce_id`, `formato_id`) univoco. MySQL accetta però più righe con `formato_id` vuoto, quindi la regola "prezzo unico oppure prezzi con formato, mai entrambi" e la regola "formato della stessa categoria della voce" le verifica il servizio, nella stessa transazione che salva la voce.

### Tabella `orari_settimanali`

Contiene il calendario settimanale: una riga per turno. Un giorno senza righe è chiuso.

| Colonna | Tipo | Significato |
|---|---|---|
| `id` | INT, chiave primaria, auto-incrementale | Identificativo numerico univoco |
| `giorno_settimana` | TINYINT, obbligatoria, da 1 (lunedì) a 7 (domenica) (CHECK) | Il giorno in cui il turno **inizia**, con la numerazione di `isoweekday()` di Python |
| `ora_inizio` | TIME, obbligatoria | Inizio del turno |
| `ora_fine` | TIME, obbligatoria, diversa da `ora_inizio` (CHECK) | Fine del turno; se è precedente a `ora_inizio`, il turno finisce il giorno dopo |

Indice: `giorno_settimana`. L'assenza di sovrapposizioni, anche tra un turno oltre la mezzanotte e il giorno dopo, la verifica il servizio (sezione 3).

### Tabella `impostazioni`

Contiene i dati del locale mostrati nelle pagine. Ha una sola riga, creata dai dati iniziali.

| Colonna | Tipo | Significato |
|---|---|---|
| `id` | TINYINT, chiave primaria, vale sempre 1 (CHECK) | Garantisce una sola riga |
| `nome_locale` | VARCHAR(100), obbligatoria | Nome mostrato sul sito |
| `indirizzo` | VARCHAR(255), obbligatoria | Indirizzo mostrato e usato per costruire il link a Google Maps |
| `telefono` | VARCHAR(20), obbligatoria | Telefono con prefisso internazionale, senza spazi (es. `+390810000000`), come serve al link `tel:`; sul sito si mostra con gli spazi |
| `telefono_di_prova` | BOOLEAN, obbligatoria, predefinito sì | Se vale sì il sito mostra "numero di prova" accanto al numero e lo esclude dal JSON-LD |
| `whatsapp` | VARCHAR(20), obbligatoria | Numero WhatsApp, stesso formato del telefono; il link `wa.me` usa solo le cifre. Separato dal telefono perché può essere un cellulare |
| `whatsapp_di_prova` | BOOLEAN, obbligatoria, predefinito sì | Se vale sì il numero WhatsApp è un segnaposto (il pulsante lo dice nel suggerimento "Numero di prova") |
| `email` | VARCHAR(255), obbligatoria | Email del locale |
| `url_facebook` | VARCHAR(255), obbligatoria | Indirizzo della pagina Facebook |
| `url_instagram` | VARCHAR(255), obbligatoria | Indirizzo del profilo Instagram |
| `fuso_orario` | VARCHAR(64), obbligatoria, predefinito 'Europe/Rome' | Fuso orario IANA usato da `zoneinfo` per "aperto ora" |

### Tabella `tentativi_accesso`

Contiene i tentativi sbagliati di login e di cambio password, per il limite di 5 al minuto (sezione 7). Sta nel database, e non nella memoria del server, perché il limite deve valere anche quando l'hosting fa girare il sito su più processi.

| Colonna | Tipo | Significato |
|---|---|---|
| `id` | BIGINT, chiave primaria, auto-incrementale | Identificativo del tentativo |
| `ambito` | VARCHAR(20), obbligatoria | `login` oppure `password` (cambio password dall'area): i due limiti sono separati |
| `impronta_ip` | CHAR(64), obbligatoria | HMAC-SHA256 dell'indirizzo IP con la `SECRET_KEY`: l'IP in chiaro non si salva |
| `tentato_il` | DATETIME(6), obbligatoria | Momento del tentativo, in UTC |

Indici su (`ambito`, `impronta_ip`, `tentato_il`) per il conteggio e su `tentato_il` per la pulizia: a ogni nuovo tentativo si cancellano quelli più vecchi di un'ora. Nessuna relazione con `utenti`: si conta per indirizzo, anche per email inesistenti.

### Dati iniziali

Li carica lo script dei dati iniziali dopo `schema.sql`. I prezzi sono stati letti a vista dal rendering del PDF `Menu_digitale.pdf` (titolo interno "Menù a parete 85,8x140,5cm 2025", modificato il 22/12/2025), non dal suo livello di testo.

**Impostazioni** (i valori marcati FITTIZIO sono segnaposto)

| Campo | Valore |
|---|---|
| `nome_locale` | SmashBroski Pompei |
| `indirizzo` | Vico dei Paninari, 7 - 80045 Pompei (NA) |
| `telefono` | +39 081 000 0000 (FITTIZIO), `telefono_di_prova` = sì |
| `whatsapp` | +39 300 000 0000 (FITTIZIO, prefisso non assegnato), `whatsapp_di_prova` = sì |
| `email` | info@example.com (FITTIZIO) |
| `url_facebook` | https://example.com/facebook-segnaposto (FITTIZIO) |
| `url_instagram` | https://example.com/instagram-segnaposto (FITTIZIO) |
| `fuso_orario` | Europe/Rome |

**Orari settimanali**

| Giorno | Turni |
|---|---|
| 1 Lunedì | 12:00–15:00, 18:00–01:00 |
| 2 Martedì | chiuso (nessuna riga) |
| 3 Mercoledì | 12:00–15:00, 18:00–01:00 |
| 4 Giovedì | 12:00–15:00, 18:00–01:00 |
| 5 Venerdì | 12:00–15:00, 18:00–01:00 |
| 6 Sabato | 18:00–02:00 |
| 7 Domenica | 18:00–02:00 |

**Categorie e formati**

| Pos. | Categoria | Slug | Formati di prezzo | Nota |
|---|---|---|---|---|
| 1 | Starters | `starters` | 5 pz, 10 pz | — |
| 2 | Salad | `salad` | Single, Menù | — |
| 3 | Burger | `burger` | Panino single hamb., Panino double hamb., Menù single hamb., Menù double hamb. | "Brooo, prova il menù: 1 panino, 1 porzione di patatine stick, 1 bibita a scelta (Coca-Cola, Fanta, Sprite o Acqua)." |
| 4 | Kids Menù | `kids-menu` | — | — |
| 5 | Soft Drinks | `soft-drinks` | — | — |
| 6 | Beers | `beers` | — | — |
| 7 | The Originals | `the-originals` | Burger, Menù | "Ortaggio su base stagionale" |

**Voci e prezzi** (in euro per leggibilità; nel database in centesimi)

*Starters*

| Pos. | Voce | Descrizione | Prezzi |
|---|---|---|---|
| 1 | Straccetti di pollo | Pollo croccante ricetta bro | 5 pz 4,00 · 10 pz 7,00 |
| 2 | Patatine stick | — | 3,00 (unico) |
| 3 | Patatine stick bacon & cheese | — | 4,00 (unico) |

Ordine diverso dal PDF (decisione del 18/10, DEVLOG): gli Straccetti, l'unica voce con i formati 5 pz e 10 pz, vengono per primi, così l'intestazione delle colonne sta subito sopra di loro e non sembra riferita ai prezzi unici delle patatine.

*Salad*

| Pos. | Voce | Descrizione | Single | Menù |
|---|---|---|---|---|
| 1 | Italian salad | Insalata, rucola, pollo alla griglia, pomodorini, scaglie di Parmigiano, crostini | 8,00 | 10,00 |
| 2 | Rocket Salad | Insalata, rucola, pollo alla griglia, noci, speck, crostini | 8,00 | 10,00 |

*Burger*

| Pos. | Voce | Descrizione | Panino single | Panino double | Menù single | Menù double |
|---|---|---|---|---|---|---|
| 1 | Smash Burger | Hamburger, insalata, pomodoro, salsa smash | 7,00 | 8,50 | 10,00 | 12,00 |
| 2 | Smash Salad | Hamburger, insalata, pomodoro, cipolla, salsa smash | 7,50 | 9,00 | 11,00 | 12,00 |
| 3 | Smash Cheeseburger | Hamburger, cheddar, salsa smash | 7,00 | 8,50 | 11,00 | 12,00 |
| 4 | Smash Bacon Cheeseburger | Hamburger, cheddar, bacon, salsa smash | 7,50 | 9,00 | 11,00 | 12,00 |
| 5 | Smash Onion Rings | Hamburger, cheddar, bacon, anelli di cipolla croccanti, salsa bbq | 8,00 | 9,50 | 11,50 | 13,00 |
| 6 | Los Pollos Classic | Pollo croccante, insalata, salsa mayo | 7,00 | — | 11,00 | — |
| 7 | Los Pollos Bacon | Pollo croccante, cheddar, bacon, salsa smash | 7,50 | — | 11,00 | — |

*Kids Menù*

| Pos. | Voce | Descrizione | Prezzo |
|---|---|---|---|
| 1 | Menù Kids Smash Baby Hamburger | Bun con hamburger, patatine e soft drink | 6,00 |
| 2 | Menù Kids Los Pollos | Bun con pollo impanato, patatine e soft drink | 6,00 |

*Soft Drinks*

| Pos. | Voce | Prezzo |
|---|---|---|
| 1 | Acqua 50cl | 1,00 |
| 2 | Coca Cola / Fanta / Sprite 33cl | 2,00 |
| 3 | Red Bull 33cl | 3,00 |

*Beers*

| Pos. | Voce | Prezzo |
|---|---|---|
| 1 | Nastro Azzurro 33cl | 2,50 |
| 2 | Heineken 33cl | 3,00 |
| 3 | Tennent's 33cl | 3,50 |

*The Originals*

| Pos. | Voce | Descrizione | Burger | Menù | Edizione | Nota |
|---|---|---|---|---|---|---|
| 1 | Scarulella Bro | Hamburger 180gr, provola, scarola, salame a listarelle | 9,00 | 13,00 | Winter Edition | — |
| 2 | Friariello Bro | Hamburger 180gr, provola e friarielli | 9,00 | 13,00 | Winter Edition | — |
| 3 | Fungitiello | Hamburger 180gr, provola impanata, melanzane a funghetto | 9,00 | 13,00 | Summer Edition | — |
| 4 | Scapece | Hamburger 180gr, zucchine alla scapece, prosciutto crudo | 9,00 | 13,00 | Summer Edition | — |
| 5 | Veggy 2.0 | Verdure di stagione, provola impanata, salsa mayo | 7,00 | 11,00 | — | Prova anche la variante con la zucca |

Totale: 7 categorie, 10 formati, 25 voci. Il primo proprietario non fa parte dei dati iniziali: si crea con `flask crea-proprietario`.

## 5. Modello a oggetti (classi e ruolo dell'OOP)

Le classi sono divise in quattro gruppi, ognuno con un solo compito. Le rotte Flask restano sottili: leggono la richiesta, chiamano un servizio e mostrano il risultato.

### Modelli

Classi definite con `@dataclass` che rappresentano una riga del database. Contengono i dati e pochi metodi semplici che li riguardano. Non eseguono query.

| Modello | Tabella | Differenze rispetto alle colonne della sezione 4 |
|---|---|---|
| `Utente` | `utenti` | Nessuna |
| `Categoria` | `categorie` | Contiene la lista dei suoi `FormatoPrezzo` e delle sue `VoceMenu` |
| `FormatoPrezzo` | `formati_prezzo` | Nessuna |
| `VoceMenu` | `voci_menu` | Contiene la lista dei suoi `PrezzoVoce`; metodo `ha_prezzo_unico()` |
| `PrezzoVoce` | `prezzi_voce` | Include anche l'etichetta del formato, letta da `formati_prezzo`, per mostrarla senza altre query |
| `Turno` | `orari_settimanali` | Metodi `supera_mezzanotte()` e `intervallo(data)`, che restituisce inizio e fine del turno come date e ore complete per una data precisa (con la fine nel giorno dopo se il turno supera la mezzanotte) |
| `Impostazioni` | `impostazioni` | Metodo `link_maps()`, che costruisce il link a Google Maps dall'indirizzo |

Oltre ai modelli delle tabelle c'è `StatoApertura` (`@dataclass`, senza tabella): il risultato del calcolo "aperto ora", con `aperto` (sì/no), il turno in corso e la `prossima_apertura`. La home e la pagina Orari e contatti lo ricevono già pronto e si limitano a mostrarlo.

Non ci sono sottoclassi: c'è un solo ruolo e le voci di tutte le categorie hanno gli stessi dati. Le differenze tra categorie (quali formati di prezzo sono ammessi) sono dati in `formati_prezzo`, non classi diverse. L'ereditarietà si usa solo per le eccezioni.

### Repository

Una classe per ogni gruppo di tabelle. Contengono tutte le query SQL, sempre parametrizzate, e trasformano le righe in modelli. Sono l'unico posto del progetto in cui si scrive SQL.

| Repository | Tabelle |
|---|---|
| `UtenteRepository` | `utenti` |
| `MenuRepository` | `categorie`, `formati_prezzo`, `voci_menu`, `prezzi_voce` |
| `OrariRepository` | `orari_settimanali` |
| `ImpostazioniRepository` | `impostazioni` |
| `TentativiRepository` | `tentativi_accesso` (contare, registrare, cancellare i tentativi vecchi; lavora con valori semplici, senza modello) |

`MenuRepository` legge il menù pubblico con poche query (categorie, formati, voci attive, prezzi) e lo ricompone in Python, senza una query per ogni voce.

### Servizi

Contengono le regole di business della sezione 3. Usano i repository e non dipendono da Flask, quindi si testano con pytest senza avviare il sito.

| Servizio | Compito |
|---|---|
| `AuthService` | Login con verifica Argon2id, controllo che l'account sia attivo, aggiornamento dell'hash quando i parametri di Argon2 cambiano, creazione del proprietario da riga di comando; cambio della password (con quella attuale), reimpostazione e attivazione/disattivazione dell'account da riga di comando |
| `MenuService` | Menù pubblico (solo voci attive, in ordine di posizione); creazione e modifica di una voce con le regole sui prezzi (prezzo unico oppure formati della sua categoria) salvate in un'unica transazione; nascondere e rimostrare una voce; conversione del prezzo scritto dal proprietario ("7,50") in centesimi |
| `TentativiService` | Limite di 5 tentativi sbagliati al minuto per IP e per ambito: blocco, registrazione con l'impronta HMAC dell'IP, pulizia dei tentativi più vecchi di un'ora. Riceve l'istante come parametro nei test, come `stato_apertura(adesso)` |
| `OrariService` | Lettura e salvataggio del calendario settimanale con il controllo delle sovrapposizioni, anche oltre la mezzanotte; calcolo di `StatoApertura` |

Il calcolo dell'apertura riceve l'istante come parametro (`stato_apertura(adesso)`) invece di leggere l'orologio: così i test controllano martedì alle 00:30 o lunedì alle 01:30 senza dipendere dall'ora in cui vengono eseguiti. La rotta gli passa l'ora attuale nel fuso delle impostazioni.

La conversione inversa, da centesimi a "7,50 €", è un filtro Jinja (`euro`), perché riguarda solo la presentazione.

### Eccezioni personalizzate

Il modulo `eccezioni.py` definisce una classe base, `SmashBroskiError`, e due eccezioni derivate:

| Eccezione | Quando | Gestione |
|---|---|---|
| `DatiNonValidiError` | Una regola della sezione 3 è violata (prezzo non valido, formato di un'altra categoria, turni sovrapposti) | Contiene l'elenco dei messaggi; la rotta mostra di nuovo il modulo con i messaggi e codice 400 |
| `NonTrovatoError` | La voce richiesta non esiste | Gestore centrale con `@app.errorhandler`: pagina 404 |

Creo una nuova eccezione solo se va gestita in modo diverso da queste. Un login sbagliato non è un'eccezione: `AuthService` restituisce `None` e la rotta mostra il messaggio generico.

## 6. Struttura del progetto Flask

### Cartelle

```
smashbroski/
├── app/
│   ├── __init__.py        # create_app(): crea e configura l'applicazione
│   ├── modelli/           # classi @dataclass
│   ├── repository/        # query SQL
│   ├── servizi/           # regole di business
│   ├── rotte/             # Blueprint, uno per area
│   ├── templates/         # pagine Jinja
│   ├── static/            # CSS, js/navbar.js, immagini WebP (logo, foto dell'hero, motivo dello sfondo)
│   ├── eccezioni.py
│   ├── limiti.py          # decoratore limita_tentativi delle rotte con password
│   ├── comandi.py         # comandi da terminale (crea-proprietario, reimposta-password, disattiva/riattiva-proprietario)
│   └── db.py              # connessione a MySQL
├── database/
│   ├── schema.sql         # creazione delle tabelle
│   ├── dati_iniziali.sql  # menù, orari e impostazioni della sezione 4
│   └── aggiornamenti/     # SQL per aggiornare un database già esistente senza ricaricarlo
├── strumenti/
│   └── prepara_immagini.py # Pillow, solo sviluppo: originali → WebP
├── tests/
├── docs/
├── DEVLOG.md
├── README.md
├── requirements.txt
├── .env.example           # nomi delle variabili con valori finti
└── run.py                 # avvio in sviluppo
```

### Blueprint

Ogni Blueprint ha un prefisso nell'URL; quello riservato ha un controllo in `before_request` che Flask esegue prima di ogni sua rotta, così una rotta aggiunta in seguito è protetta senza doverlo ricordare (regola "nega per default").

| Blueprint | Prefisso | Accesso | Rotte |
|---|---|---|---|
| `pubblico` | `/` | Tutti | `/` home, `/menu` menù, `/info` orari e contatti, `/privacy` privacy e cookie |
| `auth` | `/auth` | Tutti | `/auth/login` (GET e POST), `/auth/logout` (solo POST) |
| `proprietario` | `/proprietario` | Solo proprietario con account attivo | `/proprietario/` elenco delle voci per categoria; `/proprietario/voci/nuova`; `/proprietario/voci/<id>` modifica; `/proprietario/voci/<id>/visibilita` nascondi o rimostra (POST); `/proprietario/orari` calendario settimanale; `/proprietario/password` cambio della password (stesso limite di 5 tentativi al minuto del login) |

Un visitatore non loggato che apre una rotta di `proprietario` viene mandato al login. Con un solo ruolo non esiste il caso "ruolo sbagliato" (403).

Il menù pubblico è una sola pagina scritta dal server: l'indice in cima usa link interni (`#burger`), che funzionano senza JavaScript e senza ricaricare la pagina. Per questo non uso HTMX né un filtro in JavaScript (RNF-05, RNF-08).

L'unico JavaScript del sito è `static/js/navbar.js`: pulsante a tre linee della navbar sotto i 900 px e ora di Pompei con sole o luna. È un file del sito (CSP `script-src 'self'`, nessuno script in linea); senza JavaScript le pagine restano complete, con le voci nella barra e senza ora.

### Application factory

L'applicazione non è creata a livello di modulo, ma dalla funzione `create_app()` in `app/__init__.py`, che riceve la configurazione, registra i Blueprint, il filtro `euro`, gli header di sicurezza e il gestore delle eccezioni, e restituisce l'app. Così i test creano un'app separata con un database di prova.

## 7. Sicurezza e controllo accessi

### Autenticazione e sessione

- **Password con Argon2id** (`argon2-cffi`, classe `PasswordHasher` con i parametri predefiniti della libreria). Al login, se `check_needs_rehash()` indica parametri superati, l'hash viene ricalcolato e salvato. Lunghezza della password: da 15 a 128 caratteri (15 è il minimo del NIST SP 800-63B rev. 4 quando la password è l'unico fattore; oltre 128 è rifiutata senza calcolare l'hash, così una password enorme non fa lavorare il server). Nessuna regola di composizione (maiuscole, simboli) e nessun cambio periodico obbligatorio, come chiede il NIST. Rifiutate le password facili da indovinare: presenti in `app/dati/password_comuni.txt` (circa 11.000 password di almeno 15 caratteri dagli elenchi di SecLists), con meno di 5 caratteri diversi, o che contengono il nome del sito o la parte dell'email prima della @ (ignorando maiuscole, spazi e segni).
- **Stesso tempo di risposta per email esistenti e inesistenti**: se l'email non esiste, `AuthService` verifica comunque la password contro un hash fittizio, così dai tempi non si capisce quali email sono registrate. Il messaggio di errore è sempre generico ("email o password non corretti").
- **Login con la sessione di Flask**, senza librerie esterne: dopo il controllo della password la sessione viene svuotata e riceve solo l'`id` dell'utente e l'impronta della password (protezione dalla session fixation; `app/sessione.py`). L'impronta è un HMAC-SHA256 dell'hash Argon2 con la `SECRET_KEY` (il cookie è firmato ma leggibile, l'hash non deve finirci): a ogni richiesta il `before_request` la confronta con quella della password attuale, quindi un cambio di password (dall'area o con `reimposta-password`) chiude subito le sessioni sugli altri dispositivi. Il logout è una richiesta POST e svuota la sessione.
- **Utente ricaricato a ogni richiesta** dal `before_request` di `proprietario`: un account disattivato perde l'accesso subito.
- **Cookie di sessione** con `HttpOnly`, `SameSite=Lax` e, in produzione, `Secure`; sessione chiusa dal server dopo **1 ora di inattività** o **8 ore dal login** (OWASP WSTG e ASVS 3.3/3.4): ora del login e dell'ultima attività sono nella sessione firmata e il `before_request` le controlla. Senza questo controllo Flask rinnoverebbe il cookie a ogni richiesta e la sessione non scadrebbe mai per chi la usa.
- **Limite ai tentativi sbagliati** (`TentativiService` e decoratore `limita_tentativi` in `app/limiti.py`): al massimo 5 tentativi sbagliati al minuto per indirizzo IP sul login e, separatamente, sul cambio password, poi risposta 429 fino a quando il più vecchio esce dalla finestra di un minuto; si contano solo le password sbagliate (al login ogni errore, nel cambio password solo la password attuale sbagliata, non una conferma diversa) e le richieste rifiutate non allungano il blocco. Dopo ogni errore la pagina dice quanti tentativi restano ("Tentativi rimasti: 3 su 5.", poi "Ultimo tentativo", al quinto "l'accesso è bloccato per un minuto"): il contatore è per connessione e scende allo stesso modo per email esistenti e inesistenti, quindi non rivela quali email sono registrate. I tentativi stanno nella tabella `tentativi_accesso`, quindi il limite vale per tutti i processi del server e non si azzera a un riavvio (dal 24/10 al posto di Flask-Limiter in memoria, che con 3 processi permetteva fino a 15 tentativi). Dell'IP si salva solo un HMAC con la `SECRET_KEY`, cancellato dopo un'ora. Dietro il proxy dell'hosting l'IP vero si legge con `ProxyFix`, attivo solo se `PROXY_FIDATI` in `.env` indica quanti proxy ci sono (0 in sviluppo): senza, tutti i visitatori avrebbero l'IP del proxy e 5 errori di chiunque bloccherebbero il login a tutti; con un numero troppo alto chiunque potrebbe falsificare l'IP.
- **Nessuna registrazione pubblica**: il proprietario si crea con `flask crea-proprietario`, che chiede la password senza mostrarla (`getpass`).

### Protezione delle richieste

- **Dimensione delle richieste**: `MAX_CONTENT_LENGTH` di 64 KB, oltre la richiesta è rifiutata con 413.
- **CSRF**: `CSRFProtect` di Flask-WTF protegge tutti i moduli POST, compreso il logout.
- **SQL injection**: tutte le query usano parametri (`%s`) passati separatamente al driver.
- **XSS**: Jinja applica l'escape automatico; `|safe` non si usa mai su dati inseriti dal proprietario. Il JSON-LD si scrive con il filtro `tojson`, che rende innocui i caratteri `<`, `>` e `&`.
- **Validazione sul server** di ogni dato del proprietario: lunghezze massime come nella sezione 4, prezzi nel formato "7", "7,5" o "7,50" (virgola, mai il punto) tra 0,01 € e 999,99 €, nome della voce unico nella categoria, orari nel formato HH:MM, voce e formati della stessa categoria.

### Header di sicurezza (AU-NET07)

Un `after_request` registrato in `create_app()` aggiunge a tutte le risposte:

| Header | Valore | Scopo |
|---|---|---|
| `Content-Security-Policy` | `default-src 'self'; img-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'` | Il browser carica solo risorse del sito; il sito non può essere inserito in un frame |
| `X-Content-Type-Options` | `nosniff` | Il browser rispetta il tipo dichiarato dei file |
| `X-Frame-Options` | `DENY` | Stessa protezione di `frame-ancestors` per i browser più vecchi |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Ai siti esterni (Maps, social) arriva solo il dominio, non il percorso |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=(), usb=()` | Il browser nega queste funzioni a tutte le pagine del sito |
| `Cross-Origin-Opener-Policy` | `same-origin` | Una pagina di un altro sito aperta dal nostro non può controllare la nostra finestra |
| `Strict-Transport-Security` | `max-age=31536000` (solo in produzione) | Il browser usa sempre HTTPS |

Le pagine di `proprietario` hanno anche `Cache-Control: no-store`. Nessuna pagina contiene il meta `generator` (AU-SEO03).

### Cookie e privacy (AU-NAV12)

- Le pagine pubbliche non hanno moduli, quindi non creano la sessione: il visitatore non riceve cookie. Il cookie di sessione nasce solo aprendo il login.
- Nessuno strumento di analisi del traffico e nessuna risorsa da altri domini (font, script, mappe incorporate): Maps e i social sono semplici link.

### Segreti e configurazione

- **Segreti solo nel file `.env`**, escluso da Git e letto con `python-dotenv`: `SECRET_KEY` (lunga e casuale, generata con il modulo `secrets`) e credenziali del database. Nel repository c'è solo `.env.example`.
- **Utente MySQL dedicato all'app**, con permessi solo sul database del progetto, mai `root`.
- **Debug solo in sviluppo**: in produzione è spento e gli errori mostrano una pagina generica. `run.py` (che accende il debugger) si rifiuta di partire con `PRODUZIONE=1`; online il sito gira con un server WSGI.
- **Repository pubblico**: i comandi di gestione e l'indirizzo del login possono stare in Git; mai `.env`, password, `SECRET_KEY`, email reali degli account (neanche negli esempi), IP e dati dell'hosting, copie del database.

### Test degli accessi

Un test pytest scorre tutte le rotte registrate con prefisso `/proprietario` e verifica che un visitatore anonimo venga mandato al login. Una rotta nuova finisce nel test automaticamente.
