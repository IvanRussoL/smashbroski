# DEVLOG – SmashBroski Pompei

Diario delle scelte di sviluppo: cosa ho fatto, perché e quali alternative ho scartato.

## 2026-10-15 · Fase 0 – Audit del sito attuale

- **Audit non invasivo del sito WordPress (smashbroski.example), solo in osservazione**: DevTools (Network, Console, Issues, Coverage, Lighthouse), sorgente HTML ed emulazione dei viewport, senza inviare moduli né modificare nulla. Il sito non è mio, quindi non si fanno test che possano alterarlo o caricarlo.
- **32 casi in 5 aree (AU-NET, AU-CON, AU-UI, AU-NAV, AU-SEO), nel formato del piano di test del tirocinio** (Precondizione / Passi / Atteso, esito, evidenza): 8 PASS, 21 FAIL (7 di gravità alta), 3 BLOCKED. Tracciamento in `Audit_SmashBroski_Fase0.xlsx`, evidenze in `audit_screenshot/`. Il FAIL diventa la motivazione di un requisito del nuovo sito.
- **BLOCKED invece di un esito supposto** per i casi che richiedono uno smartphone reale (AU-UI04 barra degli indirizzi dinamica, AU-NAV08 link del telefono con WhatsApp, AU-NAV10 posizione su Google Maps): l'emulazione non riproduce quei comportamenti. Si verificano sul nuovo sito.
- **AU-NET04 (Lighthouse) PASS con LCP 2,3 s, dalla Run 3**: delle Run 1 e 2 sono registrati solo i punteggi, non LCP, CLS e TBT. Limite accettato e documentato nel foglio; nel piano di test del nuovo sito si registrano tutte le metriche di ogni esecuzione.
- **Audit e file di contesto fuori dal repository Git**: riguardano il sito di un altro e non fanno parte del codice; nel repository restano progettazione, piano di test e codice.

## 2026-10-16 · Progettazione – Obiettivo, perimetro e requisiti (sezioni 1-3)

- **Prototipo funzionante con dati reali del locale e segnaposto dichiarati**: serve a mostrare ai titolari che i FAIL dell'audit sono risolti e che il proprietario aggiorna da solo menù e orari; se la proposta viene accettata si sostituiscono i segnaposto senza riprogettare. Due traguardi: "pronto per la demo" e "pronto per la pubblicazione".
- **Perimetro: ciò che fa il sito attuale, fatto bene, più gli orari**: home, menù in HTML, area proprietario minima. Rimandati asporto e domicilio, allergeni, specialità stagionali gestite, foto dei panini, WhatsApp, prenotazioni e ordini. Alternativa scartata: aggiungere subito nuove funzioni (più lavoro prima di avere qualcosa da mostrare, e nessun FAIL che le chieda).
- **Ogni requisito indica il caso dell'audit che risolve**: il collegamento AU → RF/RNF → test rende verificabile il miglioramento ed è la base della matrice del piano di test.
- **Telefono, email e social segnaposto**: `+39 081 000 0000` con la scritta "numero di prova" ed escluso dal JSON-LD, `info@example.com`, link su `example.com`, dominio riservato agli esempi che non porta al sito di nessuno. L'indirizzo è reale perché è un dato pubblico del locale.
- **Telefono come link `tel:`, senza WhatsApp**: il sito attuale manda il numero fisso a `wa.me` (AU-NAV08) e Chrome segnala il redirect come bounce tracking (AU-CON02).
- **Link a Google Maps costruito dall'indirizzo** al posto del link breve `maps.app.goo.gl` (AU-NAV10): resta valido anche se cambia il link condiviso e si legge nel codice.
- **Categorie fisse (le 7 del PDF), gestite solo le voci**: il proprietario aggiorna voci, prezzi e orari, che sono ciò che cambia davvero; le categorie restano quelle del menù a parete.
- **Prezzi dei dati iniziali letti a vista dal rendering del PDF**, non dal suo livello di testo, che assegna i prezzi alla riga sbagliata (AU-NAV04).
- **Orari: un turno appartiene al giorno in cui inizia e può superare la mezzanotte; inizio incluso, fine esclusa**: "lunedì 18:00–01:00" si scrive e si mostra come lo dice il locale. "Aperto ora" considera anche il turno del giorno prima. Ora calcolata nel fuso Europe/Rome con `zoneinfo`, non in quello del server. Nessuna eccezione per data in questa fase. Alternativa scartata: spezzare i turni a mezzanotte (lunedì 18:00–24:00 e martedì 00:00–01:00), che mostrerebbe il martedì come aperto anche se è il giorno di chiusura.
- **Contatti e logo modificabili solo dai dati iniziali**: l'area proprietario resta minima (voci e orari).

## 2026-10-16 · Progettazione – Modello dei dati (sezione 4)

- **Prezzi in centesimi interi (`prezzo_centesimi`)**: nessun errore di arrotondamento. Alternativa scartata: FLOAT.
- **Formati di prezzo come dati (tabella `formati_prezzo`) e prezzi in righe separate (`prezzi_voce`)**: le colonne di prezzo del PDF cambiano da categoria a categoria (4 per i Burger, 2 per Salad e The Originals, nessuna per le bevande) e i Los Pollos non hanno i double. Con una riga per prezzo non ci sono colonne vuote, e ogni prezzo porta il suo formato scritto (AU-NAV04, AU-NAV06). Alternativa scartata: colonne di prezzo fisse in `voci_menu` (quasi sempre vuote e con un significato diverso per ogni categoria).
- **Regole non esprimibili con vincoli del database verificate dal servizio, nella stessa transazione**: "prezzo unico oppure formati, mai entrambi", "formato della stessa categoria della voce", turni non sovrapposti anche oltre la mezzanotte. I vincoli del database restano come ultima difesa (`CHECK`, `UNIQUE`).
- **Voci nascoste, mai cancellate (`attiva`)**: una voce stagionale si rimostra senza riscriverla.
- **Nome salvato in maiuscolo/minuscolo normale, maiuscolo del PDF applicato dal CSS**: la ricerca con Ctrl+F e la copia restituiscono "Smash Burger" (AU-NAV03, AU-NAV04).
- **DATETIME in UTC, TIME degli orari in ora locale**: gli orari sono regole di calendario ("si apre alle 18"); in UTC slitterebbero di un'ora a ogni cambio dell'ora legale.
- **`impostazioni` a riga singola (`id` sempre 1) con `telefono_di_prova`**: ogni dato ha il suo tipo e i suoi vincoli; il flag decide sia la scritta "numero di prova" sia l'esclusione dal JSON-LD.
- **Nessuna colonna `ruolo` in `utenti`**: esiste solo il proprietario.

## 2026-10-16 · Progettazione – Modello a oggetti e struttura Flask (sezioni 5-6)

- **Quattro strati: modelli (`@dataclass`), repository (solo SQL), servizi (regole), rotte (Blueprint sottili)**: stessa architettura del progetto del barbiere; l'SQL sta in un solo posto e le regole si testano con pytest senza avviare il sito.
- **Nessuna sottoclasse**: un solo ruolo e voci con gli stessi dati in tutte le categorie; le differenze tra categorie sono dati in `formati_prezzo`.
- **`stato_apertura(adesso)` riceve l'istante come parametro** invece di leggere l'orologio: i test controllano martedì alle 00:30 o lunedì alle 01:30 senza dipendere dall'ora in cui vengono eseguiti. Risultato in `StatoApertura`, che la home mostra soltanto.
- **Filtro Jinja `euro` per mostrare i prezzi**: la conversione da centesimi a "7,50 €" riguarda solo la presentazione.
- **Eccezioni `DatiNonValidiError` (400, modulo mostrato di nuovo) e `NonTrovatoError` (404), con base `SmashBroskiError`**: una nuova eccezione solo se va gestita in modo diverso. Un login sbagliato non è un'eccezione: `AuthService` restituisce `None`.
- **Blueprint `pubblico`, `auth`, `proprietario`; controllo degli accessi in `before_request` di `proprietario`**: una rotta aggiunta in seguito è protetta senza doverlo ricordare (nega per default). Con un solo ruolo non esiste il 403. Alternativa scartata: un decoratore su ogni rotta.
- **Menù come una sola pagina scritta dal server, con indice a link interni**: funziona senza JavaScript ed è indicizzabile (RNF-05, RNF-08). Alternative scartate: HTMX e filtro delle categorie in JavaScript.
- **Application factory `create_app()`**: i test creano un'app separata con un database di prova.

## 2026-10-16 · Progettazione – Sicurezza (sezione 7)

- **Password con Argon2id (`argon2-cffi`), minimo 12 caratteri, hash ricalcolato quando i parametri cambiano (`check_needs_rehash`)**.
- **Verifica della password anche per un'email inesistente, contro un hash fittizio**: i tempi di risposta non rivelano quali email sono registrate; messaggio sempre generico.
- **Login con la sessione di Flask, senza Flask-Login**: sessione svuotata e solo l'`id` dell'utente dopo il login, utente ricaricato a ogni richiesta (un account disattivato perde subito l'accesso), logout solo POST.
- **Flask-Limiter: 5 tentativi di login al minuto per IP, poi 429**; l'IP non viene salvato.
- **Nessuna registrazione pubblica né link visibile all'area riservata**: il primo proprietario si crea con `flask crea-proprietario` e la password si chiede con `getpass`.
- **CSRF con Flask-WTF, query parametrizzate, escape di Jinja (mai `|safe` sui dati del proprietario), JSON-LD con `tojson`**.
- **Header di sicurezza su tutte le risposte** (CSP, nosniff, X-Frame-Options, Referrer-Policy; HSTS solo in produzione) e `Cache-Control: no-store` nell'area riservata: risolvono AU-NET07.
- **Pagine pubbliche senza cookie, senza risorse da altri domini e senza strumenti di analisi**: il cookie di sessione nasce solo aprendo il login; Maps e social sono semplici link. Non serve un banner cookie (AU-NAV12).
- **Segreti solo in `.env`, utente MySQL dedicato, debug solo in sviluppo**.

## 2026-10-16 · Progettazione – Wireframe e grafica

- **Navbar fissa stile Habita79, rosso del menù all'85% con `backdrop-filter: blur()`**: all'85% il testo bianco resta sopra il contrasto 4,5:1 anche quando sotto passa una zona bianca. Tre link brevi (Menù, Orari, Contatti) che stanno in una riga anche a 360 px. Alternativa scartata: menù a scomparsa (serve JavaScript per tre link).
- **Hero a tutto schermo con foto del locale (entrata o interno), non dei panini**: le foto dei panini sono fuori perimetro. `<picture>` con taglio verticale e orizzontale, caricamento immediato perché è l'elemento LCP.
- **Hero con `min-height: 100dvh` e contenuto nel flusso normale della pagina**: il sito attuale usa `height: 100vh` con un blocco in `position: absolute` sopra, che copre icone e logo sugli schermi bassi, in orizzontale e con lo zoom (AU-UI01, AU-UI02, AU-UI05, AU-UI06).
- **Stato di apertura e giorno di oggi scritti per esteso**, non solo con un colore.
- **Menù con `h1`/`h2`/`h3` e prezzi in `<dl>`**: il lettore di schermo dice "Panino single, 7,00 euro" (AU-NAV05). Su desktop prezzi in colonne con l'intestazione a cascata del PDF, solo visiva (`aria-hidden`).
- **Colori campionati dal PDF del menù**: rosso `#B00C36`, blu `#1969BC`, blu scuro `#203E56`. La palette completa si decide con il CSS.
- **Pillow solo in uno script di sviluppo** che converte e ridimensiona le foto in WebP (RNF-03); il sito non elabora immagini.

## 2026-10-16 · Repository Git

- **`git init` e primo commit (`925fa81`, "Fase 1: progettazione e wireframe")** in `smashbroski/`, con `.gitignore` creato prima del primo commit: `.env`, cache di Python ed editor non entrano mai nella cronologia.

## 2026-10-16 · Progettazione – Piano di test

- **`docs/PIANO_TEST.md` nel formato del piano del tirocinio, con due righe in più per ogni caso: Origine (AU e requisiti) e Traguardo (Demo, Pubblicazione o entrambi)**: 53 casi manuali in 6 aree (TC-UI, TC-H, TC-M, TC-P, TC-S, TC-NS), 84 test pytest e la matrice AU → RF/RNF → test con tutti i 32 casi dell'audit. I PASS dell'audit restano come casi "da mantenere"; AU-NET03 (download del PDF) diventa N.A.
- **Casi limite dell'"aperto ora" solo con pytest**: mezzanotte, inizio e fine dei turni e ora legale si provano passando l'istante a `stato_apertura()`. A mano si controlla la coerenza con l'ora reale e si ottengono gli altri stati cambiando gli orari dall'area proprietario. Alternativa scartata: un'ora simulata configurabile in sviluppo (una modifica alla progettazione solo per i test manuali).
- **Esiti registrati in un foglio Excel nel formato dell'audit, da creare in Fase 2**; nel piano solo i campi da compilare. Alternativa scartata: colonne di esito dentro il file Markdown (scomodo da aggiornare a ogni esecuzione).
- **Dispositivi per i test**: emulazione di Chrome per i viewport; i casi su smartphone reale e con lettore di schermo si eseguono su un Oppo Reno 12 Pro (Chrome e TalkBack) e con NVDA sul PC. Safari iOS non è disponibile e non viene verificato.
- **Prezzi scritti con la virgola: "7", "7,5" e "7,50" accettati, il punto ("7.50") rifiutato**: la virgola è il separatore italiano dei decimali, e rifiutando il punto non si confonde "7.50" con un separatore delle migliaia. Aggiunto alle sezioni 3 e 7 di `PROGETTAZIONE.md`.
- **Nome della voce unico nella categoria, controllato dal servizio con un messaggio sul campo**: senza il controllo un doppione arriverebbe al vincolo `UNIQUE` del database come errore 500. Aggiunto alle sezioni 3 e 7 di `PROGETTAZIONE.md`.
- **Categoria con tutte le voci nascoste esclusa dal menù pubblico e dall'indice**: il cliente non trova titoli senza piatti; la categoria torna da sola quando il proprietario rimostra una voce. Aggiunto alla sezione 3 di `PROGETTAZIONE.md`. Alternativa scartata: titolo con la scritta "Al momento non disponibile" (una sezione vuota che non serve a chi legge il menù).
- **Correzione nel foglio dell'audit**: data di AU-NET02 da 2016-10-15 a 2026-10-15 (errore di battitura).

## 2026-10-17 · Fase 2 – Ambiente e struttura del progetto

- **Python 3.13.15 e MySQL 8.0.41, gli stessi del progetto del barbiere**: stesso PC e stesse versioni già provate; MySQL applica i vincoli `CHECK` dalla 8.0.16, e lo schema li usa (prezzi maggiori di 0, giorno da 1 a 7, una sola riga di `impostazioni`).
- **Ambiente virtuale `venv/` nella cartella del repository, escluso da Git**: le librerie del progetto non si mescolano con quelle di altri progetti; chi clona il repository lo ricrea con `requirements.txt`.
- **`requirements.txt` con le versioni bloccate**: le librerie usate direttamente più le dipendenze principali di Flask, come nel progetto del barbiere; chi installa ottiene lo stesso ambiente su cui passano i test. Nuove rispetto al barbiere: `argon2-cffi` 25.1.0 (password) e `Pillow` 13.0.0 (script delle immagini). `tzdata` serve su Windows, che non ha il database dei fusi orari usato da `zoneinfo`. Alternativa scartata: versioni libere (un aggiornamento di una libreria può rompere il progetto senza che il codice cambi).
- **Utente MySQL dedicato `smashbroski_app` e due database, `smashbroski` (sviluppo) e `smashbroski_test` (pytest)**: l'utente ha permessi solo su questi due database, quindi un errore sfruttato nel sito non arriva al resto del server; i test svuotano e ricaricano il loro database senza toccare i dati di sviluppo. Alternative scartate: collegarsi come `root` (permessi su tutto il server) e un solo database per sviluppo e test (ogni esecuzione dei test cancellerebbe le prove fatte a mano).
- **`.env.example` nel repository, `.env` escluso**: elenca le variabili con valori finti; password del database e `SECRET_KEY` restano solo sul PC.
- **`create_app()` che riceve la configurazione come parametro e si ferma se manca `SECRET_KEY`**: i test passano la loro configurazione senza dipendere da `.env`; senza chiave il sito non parte, invece di partire con una sessione falsificabile. `.env` lo carica `run.py`, non `create_app()`. Alternativa scartata: una chiave predefinita scritta nel codice (finirebbe su GitHub).
- **Test eseguiti con `python -m pytest` dalla cartella del progetto**, come nel progetto del barbiere: il comando aggiunge la cartella al percorso di Python, quindi `from app import create_app` funziona senza file di configurazione di pytest. Primo test: 2 casi su `create_app()`, entrambi PASS.
- **Correzioni**: hash del primo commit in questo diario (`925fa81`) e nome della cartella principale nella sezione 6 di `PROGETTAZIONE.md` (`smashbroski/`, il nome reale del repository).
