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

## 2026-10-17 · Fase 2 – Database: schema e dati iniziali

- **Database creati a parte e `schema.sql` senza `CREATE DATABASE` né `USE`**: lo stesso file si carica in `smashbroski` (da Workbench, come `root`) e in `smashbroski_test` (dalle fixture di pytest). In cima ci sono i `DROP TABLE IF EXISTS`, dalle tabelle che puntano alle altre a quelle a cui puntano, così il file riparte da zero ogni volta. Alternativa scartata: `CREATE DATABASE` dentro lo schema, come nel progetto del barbiere (per il database di test bisognava copiare il file e cambiare il nome a mano).
- **Set di caratteri `utf8mb4` e confronto `utf8mb4_0900_ai_ci`, dichiarati su database e tabelle**: accenti ed "€" corretti; i vincoli `UNIQUE` sui nomi non distinguono maiuscole e accenti, quindi "smash burger" è un doppione di "Smash Burger". Il controllo del nome unico in `MenuService` dovrà seguire la stessa regola, altrimenti il doppione arriverebbe al database come errore 500.
- **Vincoli con nome (`fk_`, `uq_`, `chk_`)**: dall'errore di MySQL si capisce subito quale regola è stata violata. In più rispetto alla sezione 4: `CHECK` sullo slug delle categorie (solo minuscole, cifre e trattini, con `REGEXP_LIKE` sensibile alle maiuscole), perché lo slug finisce negli indirizzi del menù (`/menu#kids-menu`).
- **Permessi di `smashbroski_app` diversi tra i due database**: sullo sviluppo solo `SELECT`, `INSERT`, `UPDATE`, `DELETE` (le tabelle le crea `root` con `schema.sql`); sul database di test anche `CREATE`, `DROP`, `INDEX` e `REFERENCES`, perché pytest ricrea le tabelle a ogni esecuzione. Nessun permesso sugli altri database del server. Alternativa scartata: gli stessi quattro permessi su entrambi, come nel progetto del barbiere (i test non potrebbero ricreare lo schema).
- **Dati iniziali in SQL (`dati_iniziali.sql`) e non in uno script Python**: sono i dati reali e fissi del locale, non dati inventati; in SQL si confrontano riga per riga con il PDF e si caricano sia da Workbench sia dai test. Id scritti a mano, perché i prezzi puntano a voci e formati; un commento per ogni gruppo indica i formati. Totali verificati dopo il caricamento: 1 impostazione, 10 turni, 7 categorie, 10 formati, 25 voci, 50 prezzi.
- **Dati iniziali in una transazione (`START TRANSACTION` … `COMMIT`)**: gli INSERT dipendono l'uno dall'altro; con un errore a metà non resta un menù incompleto. Il file si esegue solo subito dopo `schema.sql`, a tabelle vuote.
- **Telefono salvato senza spazi (`+390810000000`) e mostrato con gli spazi sul sito**: è la forma che serve al link `tel:` e al JSON-LD; la formattazione per la lettura riguarda solo la presentazione. Aggiornata la sezione 4 di `PROGETTAZIONE.md`. Alternativa scartata: salvarlo con gli spazi e toglierli per il link (il dato salvato dipenderebbe da come lo si vuole mostrare).

## 2026-10-17 · Fase 2 – Connessione al database e database di prova

- **`app/db.py` come nel progetto del barbiere: una connessione per richiesta, salvata in `g`, aperta al primo uso e chiusa con `teardown_appcontext`**: tutti i repository della stessa richiesta lavorano nella stessa transazione. A fine richiesta le modifiche senza `commit` vengono annullate, quindi un errore a metà non lascia dati a metà. Autocommit spento (predefinito del driver): ogni modifica va confermata dal servizio.
- **Parametri del database in `app.config`, letti da `.env` in `create_app()`**: i test cambiano solo `DB_NAME` con la configurazione passata a `create_app()`, senza modificare le variabili d'ambiente. Alternativa scartata: leggere `os.environ` dentro `crea_connessione()` e sovrascrivere `DB_NAME` nell'ambiente durante i test (come nel progetto del barbiere; funziona, ma la configurazione dell'app e quella della connessione possono divergere).
- **Database di prova ricreato una volta per esecuzione di pytest**, eseguendo `schema.sql` e `dati_iniziali.sql` con una funzione di `conftest.py` che salta i commenti e divide gli statement sul ";". La fixture si rifiuta di partire se il nome del database non finisce con `_test`: un errore nel `.env` non può cancellare il database di sviluppo. Ogni test riceve una connessione che a fine test annulla le modifiche.
- **Test eseguiti sul PC di sviluppo**: i test che usano il database richiedono il MySQL locale. Primo risultato: 5 test, 5 PASS (2 su `create_app()`, 3 sul database: database di prova, totali dei dati iniziali, una connessione per richiesta chiusa alla fine).

## 2026-10-17 · Fase 2 – Modelli

- **Modelli `@dataclass` raggruppati per argomento in quattro file**: `utente.py`, `menu.py` (`Categoria`, `FormatoPrezzo`, `VoceMenu`, `PrezzoVoce`), `orari.py` (`Turno`, `StatoApertura`), `impostazioni.py`. Le classi del menù si usano sempre insieme. Campi obbligatori prima, `id` per ultimo con valore `None` finché la riga non è salvata, come nel progetto del barbiere.
- **`Turno.intervallo(giorno)` restituisce data e ora locali senza fuso**: gli orari sono regole di calendario nell'ora del locale; `OrariService` converte l'istante attuale nel fuso delle impostazioni e confronta nell'ora locale. Al ritorno dall'ora legale l'ora che si ripete (02:00-03:00) vale per entrambe le occorrenze secondo l'orologio del locale, coerente con "chiude alle 02:00" letto sulla porta.
- **`StatoApertura` con `aperto`, `turno_in_corso` e `prossima_apertura`**: da aperto la home legge l'ora di chiusura dal turno, da chiuso la data e l'ora di riapertura; `prossima_apertura` vuota significa "orari non disponibili".
- **`Impostazioni.link_maps()` con l'URL di ricerca ufficiale di Google Maps (`/maps/search/?api=1&query=`)** e l'indirizzo codificato con `quote_plus`: un link stabile al posto di `maps.app.goo.gl` (AU-NAV10).
- **Formattazione del telefono rimandata alla home**: la regola degli spazi dipende dal numero reale, che non abbiamo ancora.
- **Test dei modelli senza database**: 5 test in `tests/test_modelli.py` (turno oltre la mezzanotte, intervallo nello stesso giorno e nel giorno dopo, prezzo unico, link a Maps), tutti PASS.

## 2026-10-17 · Fase 2 – Repository

- **Quattro repository, unico posto in cui si scrive SQL**: `UtenteRepository`, `MenuRepository`, `OrariRepository`, `ImpostazioniRepository`. Query sempre parametrizzate (`%s`), cursori con `dictionary=True` e righe trasformate in modelli. Nessun repository fa `commit`: la transazione la chiude il servizio, così una voce e i suoi prezzi si salvano insieme o per niente.
- **`MenuRepository.leggi_menu()` con 4 query fisse** (categorie, formati, voci, prezzi con l'etichetta del formato) ricomposte in Python: il numero di query non cresce con le voci. Restituisce anche le categorie senza voci visibili; escluderle dal menù pubblico è una regola di business e la applica `MenuService`.
- **Prezzi e turni salvati per sostituzione** (`sostituisci_prezzi`, `sostituisci_turni`: cancella e reinserisce): il modulo invia sempre l'elenco completo, quindi non serve capire quali righe sono cambiate. Alternativa scartata: confrontare vecchi e nuovi prezzi per aggiornare solo le differenze (più codice, nessun vantaggio con pochi prezzi per voce).
- **`esiste_nome()` confronta il nome nel database**, con la stessa regola del vincolo `UNIQUE` (senza maiuscole e accenti): il controllo del servizio e il vincolo non possono dare risposte diverse.
- **Colonne TIME convertite da `timedelta` a `time`**: il driver restituisce le TIME come durata dalla mezzanotte; `OrariRepository` le riporta al tipo usato da `Turno`.
- **Test dei repository sul database di prova**: 20 test in `tests/test_repository.py` (dati iniziali, ordine, prezzi con formato, voci nascoste, nome unico, scrittura e rilettura, testo con apici); ogni test annulla le sue modifiche a fine esecuzione.

## 2026-10-17 · Fase 2 – Eccezioni e OrariService

- **`eccezioni.py` con `SmashBroskiError`, `DatiNonValidiError` e `NonTrovatoError`**, come nella sezione 5. `DatiNonValidiError` contiene l'elenco dei messaggi: il modulo degli orari li mostra tutti insieme invece di uno per volta.
- **"Aperto ora" con i turni come intervalli di data e ora complete**: `Turno.intervallo()` trasforma "lunedì 18:00-01:00" in 19/10 18:00 → 20/10 01:00, e il controllo diventa `inizio <= adesso < fine` per ogni turno, senza casi speciali per la mezzanotte. Si guardano solo i turni di ieri e di oggi, perché nessun turno dura più di 24 ore. Alternative scartate: confrontare solo gli orari (ogni controllo diventa una serie di condizioni sulla mezzanotte) e contare i minuti dall'inizio della settimana con il modulo 10080 (funziona, ma un errore non si vede leggendo il codice).
- **Prossima apertura cercata da oggi agli 8 giorni successivi**: copre anche un solo turno a settimana appena finito, che riapre 7 giorni dopo.
- **Sovrapposizioni controllate su una settimana di riferimento più una copia spostata di 7 giorni**: il lunedì che segue la domenica esiste sulla linea del tempo, quindi domenica 18:00-02:00 e lunedì 01:00-03:00 risultano sovrapposti. Turni ordinati per inizio e confrontati con la fine più lontana vista fino a quel punto; turni adiacenti ammessi (fine esclusa).
- **Confronto nell'ora dell'orologio del locale**: l'istante, già nel fuso di Roma, perde il fuso prima del confronto. Al ritorno all'ora solare le 02:30 che si ripetono risultano entrambe chiuse, come dice il cartello "chiude alle 02:00".
- **Regole in funzioni del modulo, senza database (`calcola_stato`, `valida_turni`), e `OrariService` che le collega al repository**: i 21 casi delle sezioni 3.1 e 3.2 si provano in millisecondi senza MySQL; con il database si provano lettura, salvataggio e salvataggio rifiutato. `salva_turni` valida prima di toccare il database e salva in una transazione.
- **Ore accettate solo nel formato HH:MM a due cifre (da 00:00 a 23:59)**: rifiutati anche "24:00" e "9:00", oltre ai casi del piano; il modulo HTML con `<input type="time">` invia sempre questo formato.
- **Test**: 30 test in `tests/test_orari_service.py` (27 senza database, 3 con il database).

## 2026-10-17 · Fase 2 – MenuService

- **Prezzi scritti dal proprietario convertiti con un'espressione regolare (`^\d{1,3}(,\d{1,2})?$`)**: "7", "7,5" e "7,50" accettati, il punto rifiutato, limiti da 0,01 a 999,99 euro (sezione 7). La conversione in centesimi usa solo interi, mai numeri decimali.
- **`DatiVoce`: i dati del modulo come testi, validati dal servizio**: la rotta resta sottile e le regole si provano senza Flask. I prezzi per formato arrivano come lista di coppie (formato, prezzo) e non come dizionario, così un formato inviato due volte si riconosce e si rifiuta; un prezzo vuoto vuol dire "formato non offerto".
- **Tutti gli errori raccolti insieme** (nome, lunghezze, posizione, prezzi, formati, nome già usato) e mostrati nel modulo in una volta. La categoria non valida ferma subito la validazione, perché senza categoria non si possono controllare formati e nome.
- **Posizione vuota = in fondo alla categoria**: il proprietario che aggiunge una voce non deve conoscere le posizioni delle altre.
- **Salvataggio di voce e prezzi in una transazione**, con `rollback` su qualunque errore; la validazione avviene prima di toccare il database. In modifica la visibilità non cambia: si nasconde e si rimostra solo con `imposta_visibilita`.
- **Categorie senza voci visibili tolte da `menu_pubblico()`**, non dal repository: l'area proprietario usa `menu_completo()` e le vede sempre.
- **Nei test `commit()` non conferma niente (`ConnessioneDiTest` in `conftest.py`)**: i servizi chiamano `commit` come in produzione, ma a fine test il `rollback` annulla tutto, quindi un test che crea una voce non cambia i totali controllati da un altro. Alternativa scartata: ricaricare il database di prova prima di ogni test (lento).
- **Numero di query del menù pubblico verificato con un contatore**: lo stesso con 25 e con 35 voci.
- **Test**: 41 test in `tests/test_menu_service.py` (15 sulla conversione dei prezzi senza database, 26 con il database).

## 2026-10-17 · Fase 2 – AuthService

- **Argon2id con `PasswordHasher` di `argon2-cffi` e i parametri predefiniti della libreria** (oggi m=65536, t=3, p=4): non scelgo io i parametri, li aggiorna la libreria con le nuove versioni. Alternativa scartata: `generate_password_hash` di Werkzeug, usato nel progetto del barbiere (in questo progetto la progettazione chiede Argon2id esplicitamente).
- **Verifica eseguita anche per un'email inesistente, contro un hash fittizio calcolato all'avvio**: il tempo di risposta è lo stesso con email registrate e non, quindi dai tempi non si capisce quali email esistono. Il login restituisce `None` in tutti i casi di errore (email, password, account disattivato) senza dire quale controllo è fallito.
- **Hash ricalcolato al login quando `check_needs_rehash()` lo chiede**: un hash creato con parametri più deboli viene aggiornato la prima volta che il proprietario entra, l'unico momento in cui la password in chiaro è disponibile.
- **Hasher passato al servizio come parametro facoltativo**: in produzione si usa quello predefinito; i test ne passano uno che registra le verifiche, per controllare che la verifica avvenga anche con un'email inesistente.
- **Email salvata in minuscolo e cercata senza distinguere le maiuscole**: "Proprietario@Example.com" e "proprietario@example.com" sono lo stesso account.
- **Test**: 14 test in `tests/test_auth_service.py`, tutti con il database. Il comando `flask crea-proprietario` si scrive con le rotte di login, perché serve a provarle.

## 2026-10-17 · Fase 2 – Pagine pubbliche, header di sicurezza ed errori

- **Blueprint `pubblico` con home, menù e privacy, rotte sottili**: leggono impostazioni, orari e menù dai servizi e passano i dati ai template. L'ora attuale si legge con una funzione separata (`ora_attuale`), che i test sostituiscono per controllare la home martedì alle 10:00 o alle 00:30.
- **Template con `base.html` (navbar, footer) e una pagina per rotta**: un solo `<h1>` per pagina, `<title>` con tipo di locale e città, meta description. Nessun link visibile all'area riservata.
- **Menù con `h2` per categoria (con `id` uguale allo slug), `h3` per voce e prezzi in `<dl>`** (formato e prezzo), come nel wireframe; prezzo unico su una riga. Il maiuscolo dei nomi lo applica il CSS: nell'HTML resta "Smash Burger".
- **Stato di apertura scritto per esteso**, con "oggi" e "domani" quando la riapertura è vicina e il nome del giorno negli altri casi ("Chiuso · apre domani alle 12:00", "Chiuso · apre venerdì alle 12:00").
- **Filtri Jinja `euro`, `ora` e `telefono_leggibile`** in `app/formato.py`: la presentazione resta fuori dai servizi. Il telefono si mostra a gruppi ("+39 081 000 0000") con una regola provvisoria per i numeri italiani di 10 cifre, da rivedere con il numero reale.
- **JSON-LD `Restaurant` scritto con `tojson`**: nome, indirizzo, orari, link al menù; il telefono solo se non è di prova. `tojson` rende innocui `<`, `>` e `&`, quindi un nome con `</script>` non chiude lo script.
- **Header di sicurezza in un `after_request`** con i valori della sezione 7; `Strict-Transport-Security` solo con `PRODUZIONE=1` nel `.env`, perché in sviluppo il sito non è in HTTPS.
- **Pagina di errore del sito per 404, 405 e 500 e per `NonTrovatoError`**, con link alla home e al menù, invece delle pagine predefinite di Flask.
- **CSS provvisorio, solo per leggere le pagine**: colori del menù in variabili `:root`, navbar rossa, `scroll-margin-top` per i link interni. La grafica definitiva (navbar stile Habita79 semi-trasparente, hero con foto, logo) ha un passo dedicato; mancano ancora il file del logo e la foto del locale.
- **Test delle pagine sul database di prova**: i test che cambiano dati da guardare attraverso le pagine usano commit veri (l'app ha una connessione sua) e a fine test ricaricano schema e dati iniziali. 35 test nuovi in `test_filtri.py`, `test_rotte_pubbliche.py` e `test_header_sicurezza.py`.

## 2026-10-17 · Fase 2 – Login e area proprietario

- **Comando `flask --app app crea-proprietario`** con `click.prompt`: la password non compare sullo schermo e va ripetuta; gli errori di `AuthService` (email, password corta) escono come messaggio del comando. Nessuna pagina di registrazione.
- **Login con la sessione di Flask**: dopo la verifica la sessione viene svuotata e riceve solo l'`id` dell'utente; sessione permanente di 8 ore; cookie `HttpOnly`, `SameSite=Lax` e, in produzione, `Secure`. Ogni errore di login ha lo stesso messaggio e lo stesso codice (400). Logout solo con POST.
- **Flask-Limiter sul login: 5 tentativi sbagliati al minuto per indirizzo IP, poi 429**, come nel progetto del barbiere: si contano solo le risposte 400, quindi chi entra al primo colpo non consuma il limite. Conteggi nella memoria del processo (un solo server).
- **CSRF con `CSRFProtect` di Flask-WTF su tutti i POST**, logout compreso; un token mancante o scaduto mostra la pagina di errore del sito con codice 400.
- **Controllo degli accessi nel `before_request` del Blueprint `proprietario`** (nega per default): l'utente si rilegge dal database a ogni richiesta, quindi un account disattivato esce subito; `Cache-Control: no-store` su tutte le pagine riservate. Il test degli accessi scorre tutte le rotte registrate con prefisso `/proprietario`.
- **Nuova voce a partire dalla categoria (`/proprietario/voci/nuova?categoria=3`)**: il modulo mostra subito i formati di prezzo di quella categoria, senza JavaScript. In modifica la categoria non si cambia: i formati dipendono dalla categoria, e spostare una voce richiederebbe di reinserire i prezzi. Per spostarla si crea la voce nell'altra categoria e si nasconde quella vecchia.
- **Prezzi per formato nei campi `prezzo_<id del formato>`, letti tutti dalla rotta**: un campo manomesso con il formato di un'altra categoria arriva al servizio e viene rifiutato con un messaggio, invece di essere ignorato.
- **Modulo degli orari con righe fisse per giorno** (i turni esistenti più una riga libera, almeno due righe) e `<input type="time">`: niente JavaScript per aggiungere righe; una riga lasciata vuota non è un turno. Con un errore il modulo viene mostrato di nuovo con i dati scritti e codice 400.
- **Test**: il database di prova contiene anche il proprietario di prova (ricreato quando il database viene ricaricato); 25 test nuovi in `test_accessi.py` e `test_area_proprietario.py`, comandi da terminale compresi.
- **Comando registrato con `@with_appcontext`**: un comando aggiunto con `app.cli.add_command` non apre da solo il contesto dell'app, che serve alla connessione al database (emerso dal primo test del comando).
- **Stato di apertura con "oggi" e "domani" confermato** anche di notte: dopo la chiusura delle 01:00 di martedì la home scrive "apre domani alle 12:00". Aggiornati l'esempio di RF-03 in `PROGETTAZIONE.md` e la riga del test della home in `PIANO_TEST.md`.

## 2026-10-17 · Fase 2 – Cambio di categoria di una voce

- **La categoria di una voce si cambia dalla pagina di modifica** (sostituisce la scelta precedente di non permetterlo, per lasciare più libertà al proprietario, come chiede RF-17). Il proprietario sceglie la nuova categoria da un elenco; la pagina si ricarica con `?categoria=<id>` e mostra i formati di prezzo della nuova categoria, con un avviso. Nome, ingredienti, etichetta e nota restano compilati; i prezzi per formato si riscrivono, perché i formati della vecchia categoria non valgono nella nuova; la voce va in fondo alla nuova categoria se la posizione resta vuota. Finché non si salva la voce resta dov'è. Funziona senza JavaScript.
- **Le regole sono quelle di sempre, applicate alla nuova categoria**: `MenuService.modifica_voce` valida i formati e il nome unico nella categoria di arrivo; un prezzo con un formato della vecchia categoria viene rifiutato. 6 test nuovi (3 sul servizio, 3 sulle pagine).

## 2026-10-18 · Fase 2 – Grafica: immagini, navbar, hero e menù

- **Script `strumenti/prepara_immagini.py` con Pillow**, solo per lo sviluppo: converte gli originali (fuori da Git, in `materiale_grafico/`) in WebP dentro `app/static/img/`. Logo in due misure (480 px per l'hero, 96 px per la navbar, nitido sugli schermi ad alta densità); foto dell'hero in tre tagli centrati (verticale 900×1600 per i telefoni, orizzontale 1920×1080 e 1280×720), qualità 72, orientamento EXIF applicato e metadati non copiati. Pesi: logo 50 KB e 6 KB, foto da 32 a 59 KB (RNF-03, RNF-04).
- **Logo originale del locale (`Burger.png` dal sito attuale)**, non ridisegnato. È un marchio dei titolari: usato per la proposta, con il permesso da chiedere prima della pubblicazione (`docs/CREDITI_IMMAGINI.md`).
- **Foto dell'hero da Pexels come foto di lavoro** (Mathias Reding, piastrelle rosse e bianche con tavolino in legno): stile da fast food, il rosso del marchio, nessuna scritta né persona, parte sinistra libera per il testo. Scartate le altre candidate per scritte leggibili (neon, poster, tendaggio in giapponese) o per un'aria da caffetteria. Credito nel footer della home e in `docs/CREDITI_IMMAGINI.md`; va sostituita con una foto del locale prima della pubblicazione.
- **Palette completa: rosso `#B00C36` (insegna e menù), blu `#0963AD` e crema `#FFFAF0` (campionati dal file del logo), blu scuro `#203E56`**. Il blu del logo sostituisce il `#1969BC` campionato dal PDF, molto vicino: è il colore esatto del marchio. Sfondo delle pagine crema invece del bianco, come i muri del locale. Contrasti verificati: tutti sopra 4,5:1 (navbar 5,5, pulsante rosso 6,8, link blu su crema 5,9, testo secondario 8,4).
- **Navbar fissa rossa all'85% con `backdrop-filter: blur()` e logo piccolo**; le pagine senza hero partono sotto la navbar (`padding-top`), i link interni con `scroll-padding-top`.
- **Hero con `<picture>` come sfondo e contenuto nel flusso normale**: la foto e il velo scuro stanno sotto il contenuto, che allunga l'hero quando lo schermo è basso (`min-height: 100dvh`, non `height: 100vh`). Velo dal basso sui telefoni e da sinistra su schermi larghi in orizzontale, dove il contenuto è allineato a sinistra. Foto caricata subito (`fetchpriority="high"`, mai `lazy`) perché è l'elemento LCP. Il logo grande è dentro l'`<h1>` con testo alternativo "SmashBroski", seguito da "Hamburgeria a Pompei": un solo titolo, senza ripetere il nome sotto il logo.
- **Menù su desktop in colonne con l'intestazione dei formati (solo visiva, `aria-hidden`)**: griglia CSS con una colonna per formato, posizione presa dalla classe `colonna-<posizione del formato>` (gli stili in linea sono vietati dalla CSP); i `<dt>` restano nell'HTML per i lettori di schermo; formato mancante (Los Pollos double) con "—". Su telefono resta la lista formato-prezzo. Un prezzo unico in una categoria con formati (Patatine stick) va sotto il nome, non sotto una colonna, per non sembrare il prezzo di "10 pz" (dal 18/10 anche gli Straccetti vengono per primi: voce successiva).
- **Verifica con screenshot in tutti i viewport del piano** (360×800, 375×667, 390×600, 667×375, 844×390, 768×1024, 1366×768, zoom 200%): nessuno scroll orizzontale, nessuna sovrapposizione; logo, titolo, stato di apertura e pulsanti visibili nella prima schermata in tutti i casi, anche in orizzontale.

## 2026-10-18 · Fase 2 – Navbar stile Habita79, ora di Pompei, pagina Orari e contatti, sfondo di loghi, doppio footer

- **Navbar staccata dai bordi come Habita79**: barra fissa con margine sopra e ai lati, angoli arrotondati, vetro rosso (`rgba(176, 12, 54, 0.78)`) con `backdrop-filter: blur()`. Tre zone in una griglia `1fr auto 1fr`, così il logo resta al centro esatto: a sinistra "SmashBroski Pompei" in maiuscolo spaziato (decorativo, `aria-hidden`), al centro il logo, a destra ora e voci. Trasparenza al 78%: è il minimo che tiene il testo crema sopra 4,5:1 anche con una foto bianca dietro. Sulle pagine con fondo crema la barra è al 94%, perché al 78% il rosso sul crema diventava rosa. Scartate: lingua e icona dell'accessibilità di Habita79 (il sito è solo in italiano e il widget di accessibilità è uno strumento esterno: sarebbero comandi finti).
- **Pulsante con tre linee sotto i 900 px, con un piccolo file JavaScript (`static/js/navbar.js`)**: le linee diventano una X, il pannello di vetro scende e le voci entrano una dopo l'altra; si chiude con Esc (il focus torna sul pulsante), con un clic su una voce o fuori dalla barra, e passando a uno schermo largo. `aria-expanded` e `aria-controls` sul pulsante. Lo script aggiunge la classe `js` all'`<html>`: senza JavaScript il pulsante non compare e le voci restano nella barra. Script esterno caricato subito dopo la navbar (non `defer`), così le voci non lampeggiano nella barra prima di diventare un pannello; la CSP resta `script-src 'self'`. Con "riduci movimento" le animazioni sono spente. Alternativa scartata: `<details>` senza JavaScript (funziona, ma l'animazione di apertura e chiusura è più povera).
- **Su computer le voci restano visibili nella barra**: si valuta più avanti se metterle anche lì dentro il pulsante, come Habita79.
- **Ora di Pompei nella navbar con sole o luna, come l'ora e il meteo di Habita79**: è l'ora del locale (fuso delle impostazioni, `data-fuso` nella barra), non quella del visitatore; la calcola il browser con `Intl.DateTimeFormat` e si aggiorna allo scoccare di ogni minuto e al ritorno sulla scheda. Sole tra alba e tramonto, luna dopo il tramonto, con la formula semplificata dell'alba (declinazione del sole ed equazione del tempo) alle coordinate di Pompei: errore di qualche minuto, sufficiente per un'icona. Non usa il database, quindi compare anche nelle pagine di errore. Sotto i 380 px ora e pulsante sono più piccoli, per tenere il logo al centro. Alternativa scartata per ora: meteo vero da Open-Meteo chiamato dal server (servizio esterno fuori perimetro, con gestione dei guasti, test e informativa privacy dedicati).
- **Home solo con l'hero, orari e contatti nella nuova pagina `/info` ("Orari e contatti")**: lo stacco netto tra hero e sezioni bianche era brutto. La pagina Info mostra stato di apertura, orari della settimana con oggi evidenziato, telefono, email, Maps e social; la navbar ha "Menù" e "Orari e contatti". Il JSON-LD resta nella home. Un turno non si spezza sul trattino (`white-space: nowrap` per turno). Provata e scartata una striscia "Oggi · Dove" in fondo all'hero: ripeteva le informazioni già sotto il logo.
- **Sfondo animato di piccoli loghi su Menù e Orari e contatti, come i vasi di Habita79**: il personaggio del logo, senza scritta, in due tinte tenui (rosso e blu chiari) su crema, generato da `strumenti/prepara_immagini.py` (`prepara_motivo`, mattonella WebP da 5 KB). File che scorrono in orizzontale, a file alterne in direzioni opposte, solo CSS: si muove `transform` di livelli larghi una mattonella in più, senza salti. Fermo con "riduci movimento", nascosto ai lettori di schermo. Contenuto su un pannello crema pieno, così i loghi non passano sotto i prezzi. È un uso del marchio: rientra nel permesso da chiedere ai titolari.
- **Doppio footer come Habita79**: prima la fascia "Dove siamo" (indirizzo grande, pulsante "Come arrivare") nel blu del logo `#0963AD`, poi il footer rosso con logo, colonne (Il locale, Seguici, Informazioni) e una riga con © e crediti. Il velo in fondo all'hero diventa lo stesso blu, quindi la foto sfuma nella fascia senza bordo. Scartato il blu notte `#121C28` (quasi grigio, lontano dal marchio) e un blu più scuro della stessa tinta. Nelle pagine senza dati del locale (errori, area proprietario) la fascia e la colonna Seguici non compaiono. Nuove pagine future (es. "La nostra storia") si aggiungono come riga nella colonna "Il locale".
- **Test**: `test_rotte_pubbliche.py` aggiornato: telefono, email e orari si controllano su `/info` (2 test nuovi e uno spostato dalla home), `/info` aggiunta ai controlli su cookie, `generator`, link all'area riservata e header di sicurezza (`test_header_sicurezza`); in `test_area_proprietario.py` i due test sul salvataggio degli orari li rileggono da `/info`, perché la home non li mostra più (prima l'assert "non presente" passava anche senza controllare nulla); il test della struttura del menù guarda solo il contenuto di `<main>`, perché anche il footer ha titoli `h2`.

## 2026-10-18 · Fase 2 – Ordine degli Starters

- **Straccetti di pollo per primi, poi Patatine stick e Patatine stick bacon & cheese** (solo la colonna `posizione` in `dati_iniziali.sql`; gli id delle voci non cambiano). Con le bozze della nuova grafica del menù l'intestazione "5 pz / 10 pz" stava sopra le patatine, che hanno un prezzo unico, e non si capiva a quale voce si riferisse. Con gli Straccetti in cima l'intestazione sta subito sopra l'unica voce che la usa. Scartato: nascondere l'intestazione negli Starters (le colonne senza titolo non si leggono) o ripetere i formati accanto a ogni prezzo anche su desktop (riga più affollata). L'ordine resta modificabile dall'area proprietario con il campo posizione.
- **Test**: `test_starters_straccetti_prima_delle_patatine` in `test_menu_service.py`.

## 2026-10-18 · Fase 2 – Pagina del menù in stile "sticker a blocchi"

- **Scelta tra tre bozze statiche** (in `materiale_grafico/bozze_menu/`, fuori da Git): "cartellone digitale" (copia del cartellone in sala), "street food / sticker" ed "editoriale street". Scelta la seconda, unita alla struttura del menù attuale e ai riquadri colorati del PDF: SmashBroski è un fast food e il menù deve essere "street", mentre la home resta la presentazione più sobria.
- **Ogni categoria è un blocco-adesivo** (bordo blu scuro di 4 px, ombra piena spostata, angoli arrotondati) con i colori del PDF: Starters, Salad e Kids Menù rossi, Burger e The Originals crema con scritte blu, Soft Drinks e Beers blu. Il colore lo sceglie la classe `cat-<slug>` con variabili CSS (`--fondo`, `--tessera`…); una categoria nuova senza regole è crema. Alcuni blocchi sono ruotati di mezzo grado, come adesivi attaccati a mano.
- **Su schermi larghi (da 900 px) i blocchi sono disposti come il PDF** con `grid-template-areas`: Starters e Salad affiancati, Burger a tutta larghezza, Kids, Soft Drinks e Beers a sinistra, The Originals a destra. Una categoria aggiunta in futuro prende una riga intera in fondo. Limite accettato: se una categoria è nascosta (nessuna voce visibile), il suo posto resta vuoto.
- **Prezzi**: su desktop restano le colonne della versione precedente, con le intestazioni dei formati a pillola come nel PDF; su telefono ogni prezzo è una tessera con il formato scritto sopra. Il prezzo unico (patatine, bibite, kids) è un bollino accanto al nome, anche nelle categorie con formati, così non sembra il prezzo di una colonna. HTML per i lettori di schermo invariato (`<dl>`, intestazione `aria-hidden`).
- **Caratteri Anton (titoli) e Archivo Black (voci e prezzi), salvati in `static/fonts/`** in WOFF2 (18 KB ciascuno, solo sottoinsieme latino), licenza SIL OFL con il testo accanto ai file e crediti in `docs/CREDITI_IMMAGINI.md`. Nessun servizio esterno (Google Fonts scartato: richieste a un altro dominio, contro la CSP `default-src 'self'` e la regola "nessuna risorsa esterna" di TC-S07). `font-display: swap`: finché non sono caricati si vede il carattere di sistema. Per ora usati solo nella pagina del menù.
- **Indice a pillole fisso sotto la navbar** (`position: sticky`), che su telefono scorre in orizzontale; i titoli delle categorie hanno uno `scroll-margin-top` che tiene conto di navbar e indice. Nastro rosso inclinato "SMASH ★ BRO ★ POMPEI" decorativo (`aria-hidden`), per ora fermo. Rimandati: categoria corrente evidenziata nell'indice mentre si scorre (servirebbe un secondo file JavaScript) e nastro in movimento.
- **Lo sfondo di loghi resta visibile tra i blocchi**: tolto il pannello crema unico della pagina del menù (resta su Orari e contatti).
- **Verifica**: 185 test superati; screenshot a 360×800, 375×667, 390×600, 667×375, 844×390, 768×1024 e 1366×768, nessuno scroll orizzontale e nessun errore in Console (a parte `favicon.ico` 404, che c'era già).

## 2026-10-18 · Fase 2 – Modalità scura forzata dai browser

- **`<meta name="color-scheme" content="only light">` in `base.html` e `color-scheme: only light` in `:root`**: su un Samsung Galaxy Fold con Samsung Internet il menù compariva su fondo nero, con "MENÙ" rosa e anche i blocchi rossi e blu ricolorati. È la modalità scura forzata del browser, che ricolora da sola le pagine senza un tema scuro. La dichiarazione "solo chiaro" ferma la modalità scura automatica di Chrome. Samsung Internet, secondo la sua documentazione e i forum degli sviluppatori, con la sua modalità scura attiva ricolora comunque: lì l'unico rimedio sicuro è disattivarla nel browser. Verificato sul Fold: con la dichiarazione servita la pagina restava scura; spenta la modalità scura di Samsung Internet, colori del marchio corretti. Accettato come limite noto del browser (chi la tiene attiva vede scuri tutti i siti) e annotato in TC-UI12. Scartato per ora: un tema scuro vero (`prefers-color-scheme: dark`), che raddoppia i colori da mantenere e i controlli di contrasto e che Samsung Internet usa solo con un'impostazione sperimentale.

## 2026-10-21 · Fase 2 – Pagina Orari e contatti in stile "location page"

- **Scelta tra tre bozze statiche** (fuori da Git): "stato in cima + griglia a tessere", "tipografia street food" e "location page con accenti brutal". Scelta la terza: struttura ordinata come le pagine dei singoli locali delle catene di burger (indirizzo, telefono, orari, come arrivare), con bordi blu notte di 2 px e ombre piene spostate, gli stessi degli adesivi del menù, così le due pagine interne si somigliano. Home e menù non cambiano.
- **Tre azioni grandi subito sotto lo stato di apertura: Chiama (`tel:`), Indicazioni (Google Maps), Scrivi (`mailto:`)**, alte almeno 72 px, con icona SVG nel codice (`aria-hidden`) e testo sempre scritto. Al tocco il pulsante si "schiaccia" (l'ombra sparisce), con "riduci movimento" senza transizione.
- **Stato di apertura come etichetta a bordo spesso**: verde chiaro se aperto, rosa se chiuso, con il testo di `descrivi_stato_apertura` (il colore non è l'unica informazione). Solo nella pagina Info: la pillola dell'hero in home resta com'era.
- **Orari come tabella a bordo spesso con la riga di oggi in blu notte** (testo crema in grassetto), stesso HTML di prima (`<dl>` con un `<div>` per giorno, "(oggi)" scritto), quindi i lettori di schermo non cambiano. Su computer orari e "Come arrivare" sono affiancati, i contatti sono tre riquadri in riga.
- **Titoli in Anton** (già salvato in `static/fonts/` per il menù), nessuna risorsa esterna.
- **Nessuna mappa incorporata**: l'iframe di Google Maps carica cookie di terze parti (contro RNF-11) e andrebbe aperto nella CSP. Resta il link costruito dall'indirizzo. Rimandate a quando i titolari le forniscono: indicazioni scritte (stazione, parcheggio) ed eventuale immagine statica della mappa.
- **CSS toccato solo nel blocco "Pagina Orari e contatti"** e nelle due media query che lo riguardano; le classi della vecchia pagina (`.sezione`, `.orari`, `.contatti`, `.social`) sono usate solo qui, `.segnaposto` (usata anche dalla privacy) è invariata.
- **Test**: `test_info_azioni_rapide` (i tre link nella barra delle azioni) e `test_info_sezioni_e_ancore` (ancore `#orari`, `#come-arrivare`, `#contatti`, nessun iframe); `test_info_oggi_evidenziato` controlla anche che la riga evidenziata sia una sola. 187 test superati. Screenshot a 360×800 e 1366×768, senza scroll orizzontale.

## 2026-10-21 · Fase 2 – Orari e contatti come il menù, niente "Torna all'indice", scroll più fluido

- **Pagina Orari e contatti senza pannello crema**: come nel menù, ogni parte è un blocco-adesivo libero sopra lo sfondo di loghi (bordo blu notte di 4 px, ombra piena di 7 px, angoli di 16 px). Titolo su etichetta inclinata come "Menù"; indirizzo e stato in un blocco crema; Orari crema, Come arrivare rosso (appena ruotato), Contatti blu con tessere crema. Tolta la regola `.sfondo-loghi ~ .pagina-info` del pannello.
- **Tolti i link "↑ Torna all'indice" in fondo alle categorie del menù** (e le due regole `.torna-indice`): l'indice a pillole è già fisso sotto la navbar.
- **Scroll a scatti nel menù: misurato prima di correggere.** Script Playwright con CPU rallentata 20 volte, rotella su e giù per 3 s, fotogrammi contati con `requestAnimationFrame`: circa 40 fps con lo sfondo animato, circa 59 senza animazione, poco cambiava togliendo solo la sfocatura della navbar o riducendo le 16 file a 2 livelli con maschera. La causa principale sono le 16 file di loghi in movimento durante lo scroll.
- **Le file di loghi si fermano mentre la pagina scorre** (`static/js/sfondo.js`, incluso da `_sfondo_loghi.html`: classe `scorrendo` sull'`<html>` all'evento `scroll` passivo, tolta 200 ms dopo l'ultimo; in CSS `animation-play-state: paused`). Dopo la modifica circa 57-59 fps su menù e info. Senza JavaScript lo sfondo si muove come prima. Scartati: sfondo fermo sempre (si perde l'effetto scelto), file ridotte a due livelli con `mask` (guadagno piccolo, CSS più complesso).
- **Niente `backdrop-filter` sulla navbar delle pagine interne**: al 94% di opacità la sfocatura non si vede, ma sopra lo sfondo animato andava ricalcolata a ogni fotogramma. Nell'hero della home il vetro sfocato resta.
- **Verifica**: 187 test superati; screenshot a 360×800 e 1366×768 di menù e info, nessuno scroll orizzontale. La fluidità va confermata sul PC di Ivan e sull'Oppo Reno 12 Pro.

## 2026-10-21 · Fase 2 – Indice del menù: categoria attiva e atterraggio preciso

- **La pillola della categoria che si sta guardando è evidenziata (rossa), sia dopo il tocco sia scorrendo** (`static/js/indice.js`, `aria-current="location"`): è attivo il blocco più in basso che ha già raggiunto la linea appena sotto le pillole, quindi all'apertura è attivo Starters. Se due blocchi stanno alla stessa altezza (Starters e Salad su desktop) vince quello toccato. Su telefono l'indice scorre in orizzontale per tenere in vista la pillola attiva. Aggiornamento a ogni `scroll` passivo, al massimo una volta per fotogramma. Senza JavaScript l'indice funziona come prima, senza evidenziazione.
- **Hover dell'indice solo con il mouse (`@media (hover: hover)`)**: sui telefoni il tocco lasciava la pillola rossa anche dopo, e sembrava ancora attiva quella toccata.
- **Atterraggio preciso al tocco**: lo `scroll-margin-top` dei titoli delle categorie contava di nuovo la navbar, già tolta dallo `scroll-padding-top` dell'html, e il blocco atterrava circa 85 px sotto le pillole (100-112 px su desktop). Ora `6.25rem`: il bordo del blocco arriva 8-13 px sotto le pillole in tutte le categorie, misurato con Playwright a 360×800 (tocco) e 1366×768 (clic).
- **Errori 400 nel terminale aprendo il sito dal telefono**: sono richieste HTTPS (handshake TLS, i byte `\x16\x03\x01`) che il browser del telefono prova sul server di sviluppo, che parla solo HTTP; il browser poi ripiega su HTTP e la pagina funziona. Non dipendono dall'app: HSTS si invia solo con `PRODUZIONE=1` e la CSP non ha `upgrade-insecure-requests`. Si possono ignorare.
- **Cambio di categoria anticipato durante lo scroll** (segnalazione di Ivan: scorrendo piano, Burger restava attivo con Kids Menù già quasi tutto in vista). La linea che decide la categoria attiva non è più subito sotto le pillole ma al 40% dello spazio tra le pillole e il fondo dello schermo: il cambio arriva quando la categoria nuova occupa la parte alta della pagina. Misura a 360×800, scorrendo di 80 px alla volta: la pillola attiva era diversa dal blocco più visibile in 23 posizioni su 70, ora in 6 (tutte nei passaggi tra due blocchi). Su desktop il confronto conta poco, perché due colonne stanno affiancate: a pari altezza resta attiva la colonna di sinistra.
- **Il tocco resta preciso**: dopo un tocco la pillola toccata resta attiva finché il suo blocco sta dove è atterrato (fino a 48 px sotto le pillole), così un blocco corto non passa subito la mano al successivo con la linea più bassa. Atterraggio invariato: 8-13 px sotto le pillole, pillola giusta in tutte le categorie.
- **Test**: `test_menu_indice_senza_torna_indice`. 188 test superati.

## 2026-10-21 · Fase 2 – Facciata disegnata nel riquadro dello stato

- **Sfondo del riquadro "indirizzo e stato" della pagina Orari e contatti: facciata del locale disegnata in SVG** (`templates/_facciata.html`) nei colori del sito: insegna rossa "SMASHBROSKI", tenda a strisce, due vetrine e porta. Ivan aveva proposto la foto dell'esterno presa da internet: scartata, perché non abbiamo i diritti per pubblicarla e le foto di `foto_smash` sono solo riferimento, mai nel sito né in Git. La facciata si potrà sostituire con una foto dei titolari quando ci daranno il permesso.
- **Due stati, scelti dal server con la classe `locale-aperto` / `locale-chiuso`** (stesso `stato.aperto` del testo): aperto, porta aperta (l'anta gira sul cardine), vetrine e ingresso illuminati e persone che arrivano dai lati ed entrano; chiuso, porta chiusa con il cartello "CHIUSO", luci spente, nessuna persona. Lo stato resta scritto nel riquadro crema sopra la facciata: il disegno è `aria-hidden`.
- **Persone fuori dall'SVG**: la prima versione le animava dentro l'SVG e lo scroll della pagina scendeva a 41-46 fps con la CPU rallentata 20 volte (52-57 senza facciata). Ora ogni persona è un `<div>` largo quanto il riquadro che si sposta solo con `transform` e `opacity` (`will-change`): 52-53 fps, come senza facciata. Si fermano durante lo scroll (classe `scorrendo`) e con "riduci movimento" non compaiono.
- **Impaginazione**: su telefono facciata in alto e testo sotto; da 768 px facciata su tutto il riquadro e testo a sinistra, largo al massimo 15,5 rem per non coprire la vetrina.
- **Test**: `test_info_facciata_segue_lo_stato` (martedì 10:00 chiuso, mercoledì 13:00 aperto). 189 test superati.

## 2026-10-21 · Fase 2 – Mini-hero con foto al posto della facciata

- **La facciata disegnata non è piaciuta a Ivan**: voleva uno sfondo realistico come Habita79. Il riquadro "indirizzo e stato" diventa una mini-hero: foto a tutto riquadro, velo scuro dal basso, nome del locale in Anton, indirizzo e stato in crema sopra. Tolti `_facciata.html` e le persone animate (e il CSS relativo).
- **Aperto / chiuso**: stessa classe `locale-aperto` / `locale-chiuso` di prima. Da chiuso la foto perde i colori e si scurisce (`filter`, transizione di 0,6 s, niente transizione con "riduci movimento").
- **Foto provvisoria**: è la stessa foto di lavoro della hero (Mathias Reding, Pexels), versione verticale su telefono e orizzontale da 768 px, caricata in modo lazy. Una foto dell'esterno da Pexels non si è potuta scaricare (rete bloccata nell'ambiente di lavoro): da sostituire con una foto scelta da Ivan o scattata da lui, con il permesso di pubblicarla. Le foto di `foto_smash` restano solo riferimento.
- **Test**: `test_info_mini_hero_segue_lo_stato` al posto del test sulla facciata. 189 test superati (MariaDB con schema adattato; da rilanciare su MySQL 8).

## 2026-10-21 · Fase 2 – Insegna al neon e orari a strisce (in prova)

- **Foto accantonata da Ivan**: niente foto né video per ora. Tolta la mini-hero e il credito della foto; si gioca con i colori del sito. Proposti 5 modi, Ivan ha scelto di provare l'insegna al neon e gli orari a strisce e deciderà se tenerli. Il giallo cheddar come quarto colore è scartato per ora (pagina troppo colorata), ma resta un'idea.
- **Insegna al neon nel riquadro dello stato**: fondo blu scuro e APERTO / CHIUSO grande in Anton. Da aperto è accesa con bagliore rosso e si accende una volta con due sfarfallii (niente animazione con "riduci movimento"); da chiuso è spenta, solo il contorno. L'insegna è `aria-hidden`: lo stato vero resta nell'etichetta sotto.
- **Orari a strisce come la tenda**: righe alternate rosse e crema, oggi in blu scuro con il bollino rosso "OGGI" ruotato al posto di "(oggi)".
- **Test**: `test_info_insegna_segue_lo_stato` e il bollino in `test_info_oggi_evidenziato`. 189 test superati.
- **Insegna con il nome invece di APERTO / CHIUSO** (Ivan: l'insegna e l'etichetta col pallino dicevano la stessa cosa due volte). Sul neon ora c'è il nome del locale, acceso se aperto e spento se chiuso; lo stato a parole resta solo nell'etichetta. L'insegna prende il posto del vecchio nome in piccolo (`info-locale`, tolto) e non è più `aria-hidden`. Gli orari a strisce piacciono a Ivan e restano.

## 2026-10-22 · Fase 2 – Grandezze della pagina Orari e contatti ridotte

- **Perché**: per Ivan sezioni troppo grandi su telefono e desktop, soprattutto l'insegna al neon (300 px di altezza su un telefono da 800). Proposta mostrata prima come anteprima prima/dopo, approvata da Ivan.
- **Riferimenti**: testo a 16 px; titoli principali 28-36 px su telefono e 40-56 su desktop (scala 1,2-1,25, Cloud Four e Design Shack); aree di tocco di almeno 44 px (Apple, WCAG 2.5.5) o 48 (Material).
- **Nuovi valori (telefono / da 768 px)**: titolo pagina 32 / 44 px (prima 40 / 58); insegna 32-40 / 64 px su una riga (prima 61 / 112), riquadro alto 178 / 200 px (prima 300 / 320) senza altezza minima; titoli di sezione 28 / 32 px (prima 42); pulsanti Chiama, Indicazioni e Scrivi 60 / 64 px (prima 78); righe degli orari alte 44 px con i due turni su una riga (14 px su telefono, 15 da 768 px), prima 71 px su due righe. Spazi tra i blocchi a 8-16-24 px.
- **Effetto**: su telefono i pulsanti finiscono a 421 px dall'alto invece che a 589, gli orari si vedono già all'apertura; pagina più corta di circa 300 px su telefono e 220 su desktop.
- **Scartato**: turni degli orari su due righe su telefono (raddoppia l'altezza della tabella); testo degli orari sotto i 14 px.
- **Test**: nessun test nuovo (solo CSS). 189 test superati.

## 2026-10-22 · Fase 2 – Favicon con la mascotte del logo

- **Icona nella scheda del browser** (richiesta di Ivan, come Habita79): la mascotte del logo SmashBroski, blu su quadrato crema arrotondato, in tutte le pagine (`base.html`). Senza la scritta "SmashBroski": a 16-32 px non si leggerebbe.
- **File** in `static/img/`: `favicon.ico` (16, 32 e 48 px), `favicon-32.png` e `apple-touch-icon.png` (180 px, quadrato pieno, per l'icona sulla schermata home del telefono). Ricavati da `logo-hero.webp`; nelle versioni piccole i contorni blu sono ingrossati, altrimenti spariscono.
- **Rotta `/favicon.ico`**: i browser la chiedono alla radice anche senza il `<link>`; prima dava 404 (l'unico errore in Console).
- **Test**: `test_favicon`. 190 test superati.

## 2026-10-22 · Fase 2 – Home: un solo "Come arrivare"

- **Tolto il pulsante "Come arrivare" dalla fascia "Dove siamo" della home** (segnalazione di Ivan): ripeteva quello accanto a "Guarda il menù", visibile subito sopra nella stessa schermata. Il pulsante sta in un blocco Jinja (`footer_come_arrivare` in `base.html`) che la home svuota; in Menù e Orari e contatti la fascia lo tiene, perché lì non c'è l'hero. L'indirizzo resta nella fascia.
- **Test**: `test_home_come_arrivare_una_volta`. 191 test superati.

## 2026-10-22 · Fase 2 – Zoom più pulito su telefono e computer

- **Zone vuote per un attimo durante lo zoom con due dita** (segnalazione di Ivan, Oppo Reno 12 Pro con Chrome, pagine Menù e Orari e contatti, screenshot): rimpicciolendo veloce si vedeva solo un pezzo della pagina e il resto color crema. È Chrome che non fa in tempo a ridisegnare le zone appena entrate nello schermo; i sedici livelli animati dello sfondo di loghi gli tolgono memoria e tempo. Ora `sfondo.js` ascolta il `resize` di `visualViewport` (lo zoom con due dita) e mette la classe `zoom` sull'`<html>`: le file si fermano e perdono il livello proprio (`animation: none; will-change: auto`) finché la pagina resta ingrandita, e ripartono 400 ms dopo il ritorno a grandezza normale. Non verificabile sul telefono vero da qui: da confermare da Ivan. Limite noto: un minimo di ridisegno durante zoom molto rapidi è normale in Chrome.
- **Zoom con Ctrl +/- su computer**: oltre il 150% circa la pagina scende sotto i 900 px e la navbar passa al pulsante a tre linee; il passaggio partiva con le animazioni del pannello (voci che "volavano"). Ora `navbar.js` mette per 400 ms la classe `senza-animazioni` al cambio di larghezza e il CSS spegne le transizioni della navbar.
- **Scartato**: bloccare lo zoom (`user-scalable=no`, `maximum-scale=1`): serve a chi vede male (WCAG 1.4.4).
- **Test**: nessun test nuovo (solo JavaScript e CSS); controllato con Playwright che le classi si mettono e si tolgono al cambio di dimensione, senza errori in Console. 191 test superati.

## 2026-10-22 · Fase 2 – Icone nei contatti e nei titoli della pagina Orari e contatti

- **Richiesta di Ivan**: rendere più moderna la parte sotto l'insegna senza togliere nulla. Una prima proposta (orari in tabella Pranzo/Cena, contatti come lista di azioni al posto dei pulsanti, niente fascia "Dove siamo") è stata scartata: i pulsanti Chiama/Indicazioni/Scrivi, il riquadro Come arrivare, i contatti e il doppio footer blu e rosso restano.
- **Contatti con icona**: ogni riquadro ha a sinistra un quadratino rosso (blu per i social) con bordo e ombra piena come gli adesivi, con cornetta, busta e cuore. L'icona sta dentro il `<dt>` e si posiziona con `position: absolute` rispetto al riquadro, perché in una `<dl>` il `<div>` può contenere solo `dt` e `dd`. Icone SVG nel codice, `aria-hidden`.
- **Social come pillole** con il logo di Facebook e Instagram, alte 44 px (area di tocco).
- **Icone nei titoli**: orologio per Orari, segnaposto per Come arrivare, fumetto per Contatti (`.titolo-icona`, grandi 0,9 em del titolo).
- **Test**: nessun test nuovo (markup e CSS); 191 test superati.

## 2026-10-22 · Fase 2 – Striscia chiara in fondo alla home su browser con barra galleggiante

- **Segnalazione di Ivan (screenshot dal telefono)**: in home, in fondo allo schermo, sotto l'hero e dietro la barra del browser "galleggiante" in basso, compariva una fascia color crema. Questi browser (Safari 26 e altri con la barra a pillola) colorano lo spazio sotto la barra con il fondo della pagina, che era crema, mentre subito sotto l'hero c'è la fascia blu "Dove siamo".
- **Rimedio**: fondo del `<body>` della home nel blu della fascia (`body.pagina-home`), lo stesso colore in cui sfuma il velo dell'hero. Le pagine interne restano crema, che è già il loro fondo. Non verificabile da qui con quel browser: da confermare da Ivan.
- **Test**: 191 test superati (solo CSS).

## 2026-10-22 · Fase 2 – Sentiero "mappa del tesoro" nel titolo Come arrivare

- **Richiesta di Ivan** (con un'immagine di riferimento di una mappa del tesoro): dopo "Come arrivare" un piccolo sentiero tratteggiato che si disegna lentamente fino a una X, in loop.
- **Come funziona**: SVG nel titolo (`aria-hidden`). Il tratteggio (`stroke-dasharray: 4 5`) è coperto da una maschera: un tratto pieno con `pathLength="100"` la cui `stroke-dashoffset` va da 100 a 0, così il tratteggio compare poco alla volta. Ciclo di 5 s: 3 s di disegno, la X compare con un piccolo rimbalzo, 2 s di pausa e si riparte. Solo CSS, niente JavaScript. I tempi si cambiano in `sentiero-disegna` e `sentiero-x` (durata 5 s, arrivo al 60%).
- **Spazio**: il titolo non va più a capo; il sentiero prende lo spazio rimasto (su telefono è più corto, la X resta in vista). Con "riduci movimento" sentiero e X sono fermi e completi.
- **Test**: 191 test superati (markup decorativo e CSS).
- **Tempi rivisti da Ivan dopo la prova**: disegno da 3 a 2 s, pausa invariata di 2 s; ciclo di 4 s con arrivo alla X al 50%.
- **Seconda prova di Ivan**: disegno a 1,5 s, pausa 2 s; ciclo di 3,5 s con arrivo alla X al 43%.

## 2026-10-22 · Fase 2 – Indice del menù su desktop: pillole accese per riga

- **Segnalazione di Ivan (screenshot da desktop)**: scorrendo il menù la pillola "Salad" non si accendeva mai. Su desktop Starters e Salad stanno sulla stessa riga e iniziano alla stessa altezza, quindi l'indice sceglieva sempre la prima; lo stesso per The Originals, accanto a Kids Menù, Soft Drinks e Beers.
- **Scelta di Ivan: accendere insieme le categorie affiancate**. `indice.js` sceglie la categoria principale come prima (linea al 40%) e accende anche quelle in un'altra colonna che le stanno accanto in altezza: Starters + Salad, poi Kids Menù / Soft Drinks / Beers ciascuna con The Originals. Dopo un tocco su una pillola si accende solo quella. Alternative scartate: lasciare com'era (Salad raggiungibile solo col tocco) e una categoria per riga anche su desktop (pagina molto più lunga, impaginazione del PDF persa).
- **Telefono invariato**: lì le categorie sono in una sola colonna, quindi non ci sono categorie affiancate. Verificato con Playwright a 360×800: la sequenza delle pillole accese scorrendo è identica a prima del cambio.
- **Test**: 191 test superati (solo JavaScript); prova nel browser a 1440×900 e 360×800.

## 2026-10-22 · Fase 2 – Tolto "Apri in Google Maps" dalla pagina Orari e contatti

- **Richiesta di Ivan**: il pulsante "Apri in Google Maps" nel riquadro Come arrivare era ridondante, perché apre lo stesso link del pulsante "Indicazioni". Tolti il link da `info.html` e la regola `.azione-mappa` da `stile.css`; il riquadro mostra solo titolo, sentiero e indirizzo.
- **Indicazioni resta nella riga in alto** (Chiama · Indicazioni · Scrivi) finché non si sceglie dove spostarlo: la prova con la pillola al neon accanto alla X del sentiero è stata scartata su telefono (troppe scritte in poco spazio).
- **TC-H05** aggiornato: il terzo link da controllare è "Indicazioni" di `/info`.

## 2026-10-22 · Fase 2 – Pagina Orari e contatti come una lavagna

- **Idea di Ivan** (con la foto di una lavagnetta da esterno di una hamburgeria): tutto il contenuto della pagina su un'unica lavagna, senza cornice di legno. Prima c'erano blocchi-adesivo separati (insegna, azioni, orari, Come arrivare, contatti).
- **Prove scartate prima della lavagna**: pulsante Indicazioni come pillola al neon accanto alla X del sentiero (sul telefono troppe scritte in poco spazio) e poi sotto l'indirizzo (non convinceva).
- **Fondo blu scuro del marchio** (#203E56) con macchie chiare sfumate fatte di soli gradienti, come una lavagna cancellata più volte. Scartato il nero ardesia: meno "nostro". Niente disegnini a gesso per ora.
- **Titoli a gessetto, resto in grassetto normale** (Cabin Sketch, licenza SIL OFL, salvato in `static/fonts`): su due anteprime Ivan ha scelto questa contro "tutto in Anton grassetto" per una pagina più semplice ed elegante. Il gessetto resta solo nei titoli: un carattere decorativo su testi lunghi, numeri e pulsanti piccoli si legge peggio.
- **Insegna al neon in cima, a sinistra**: centrata andava bene da sola, ma sotto è tutto allineato a sinistra (indirizzo, stato, pulsanti, orari); con il neon a sinistra la lavagna ha un solo margine.
- **Tolto il riquadro Come arrivare** con il suo indirizzo e il sentiero animato: l'indirizzo è già sotto l'insegna e il pulsante Indicazioni nella riga in alto. Le guide sui siti dei ristoranti chiedono indirizzo, orari, telefono e indicazioni subito in vista, non ripetuti.
- **Contatti sotto gli orari** (scelta di Ivan); su computer gli orari restano larghi al massimo 34rem, così le ore non finiscono lontane dai giorni.
- **Pulizia del CSS**: la sezione della pagina è riscritta per la lavagna (variabili `--gesso*`, classi `lavagna`, `lavagna-testata`, `lavagna-sezione`); tolte le regole di blocchi-adesivo, righe a strisce, sentiero e Come arrivare.
- **Test**: aggiornati i controlli della pagina (lavagna presente, niente `#come-arrivare`); 191 test superati; nessuno scorrimento orizzontale da 360 a 1920 px.

## 2026-10-22 · Fase 2 – Pulsante WhatsApp al posto di "Scrivi"

- **Richiesta di Ivan**: nella riga di pulsanti in cima alla lavagna, WhatsApp sostituisce "Scrivi" (email). WhatsApp era fuori perimetro dalla progettazione (16/10); ora rientra perché lo chiede Ivan, limitato a questo pulsante.
- **Numero WhatsApp separato dal telefono** (colonne `whatsapp` e `whatsapp_di_prova` in `impostazioni`): il sito attuale manda il numero fisso a `wa.me` (AU-NAV08), che su un fisso di solito non ha WhatsApp. Il telefono resta un link `tel:` e non porta mai a WhatsApp (RF-04). Alternativa scartata: riusare il telefono.
- **Segnaposto dichiarato** `+39 300 000 0000`: il prefisso cellulare 300 non è assegnato, quindi il link non apre la chat di una persona vera. `whatsapp_di_prova` vale sì e il pulsante mostra il suggerimento "Numero di prova". Quando i titolari danno il numero si cambiano le due colonne nei dati iniziali, senza toccare template e CSS.
- **Link `https://wa.me/<cifre>`** costruito da `Impostazioni.link_whatsapp()`: è il formato ufficiale di WhatsApp e vuole solo le cifre, senza "+" né spazi. Da ricontrollare su smartphone reale con TC-H03, anche per l'avviso di Chrome sul redirect (AU-CON02).
- **L'email non sparisce**: resta come link `mailto:` nei contatti sotto gli orari (RF-05). Il pulsante WhatsApp resta color gesso come era "Scrivi"; il verde WhatsApp non è nella palette del menù.
- **Database da ricreare in locale**: `schema.sql` e `dati_iniziali.sql` hanno le nuove colonne.

## 2026-10-22 · Fase 2 – Giorno di oggi sottolineato da un'onda di gesso

- **Segnalazione di Ivan**: il riquadro rosso intorno al giorno di oggi aveva un bordo di 2 px contro l'1 px dei puntini tra i giorni, e su telefono il bollino OGGI mandava a capo il nome: la riga diventava più alta delle altre e i puntini sopra e sotto restavano scoperti.
- **Scelta di Ivan su tre anteprime** (sottolineatura a gessetto, cerchio a mano sul nome, freccia a lato): sottolineatura, ma spessa, ondulata e in movimento lento. Il giorno e i suoi orari diventano rosa gesso e al posto dei puntini sotto la riga c'è un'onda di 3 px (`static/img/onda-gesso.svg`).
- **Una sola onda lunga, non ripetuta**: la prima versione ripeteva in orizzontale un SVG di una sola onda, e Ivan vedeva dei tagli tra una copia e l'altra (con zoom non interi i bordi delle copie cadono a metà pixel). Ora l'SVG è un unico tracciato di 50 onde (1200 px, più largo della tabella orari) e non si ripete.
- **Animazione**: l'onda scorre di una lunghezza d'onda (24 px) ogni 3 secondi, così il loop non ha salti. Ferma con `prefers-reduced-motion: reduce`. SVG come file e non come `data:` URI perché la CSP ha `img-src 'self'`.
- **Bollino OGGI tolto alla vista**: la parola "oggi" resta nel `<dt>` con la classe `visivamente-nascosto`, quindi i lettori di schermo la leggono ancora. Tutte le righe hanno la stessa altezza.
- **Test**: aggiornati i due controlli sulla parola "oggi"; 192 test superati; nessuno scorrimento orizzontale a 360 e 1366 px.

## 2026-10-22 · Fase 2 – Tolto "Come arrivare" dalla fascia "Dove siamo" di Orari e contatti

- **Richiesta di Ivan**: nella fascia blu "Dove siamo" in fondo alla pagina il pulsante "Come arrivare" era superfluo, perché in cima alla lavagna c'è già "Indicazioni" con lo stesso link a Google Maps.
- **Stesso meccanismo della home**: `info.html` svuota il blocco `footer_come_arrivare` di `base.html`; la fascia resta con l'etichetta e l'indirizzo. Sulla pagina Menù il pulsante resta finché Ivan non decide.
- **Test**: `test_home_come_arrivare_una_volta` controlla anche che `/info` non abbia `pulsante-footer`; 192 test superati.

## 2026-10-22 · Fase 2 – Contatti di Orari e contatti come righe da toccare

- **Segnalazione di Ivan**: icone e pulsanti dei contatti non erano centrati né distanziati bene. Due cause: l'icona di "Social" era centrata in verticale su un blocco più alto (etichetta + due pillole), quindi scendeva rispetto alle altre; su computer le tre colonne erano larghe uguali anche se le pillole social occupavano più spazio.
- **Scelta di Ivan su cinque anteprime** (lista allineata, tessere, righe come gli orari, pillole in fila, biglietto centrato): righe come gli orari. Ogni contatto è un'unica riga-link (`<ul class="contatti">` con un `<a class="contatto">` per riga) divisa in una griglia icona | etichetta e valore | freccia ›, con la linea puntinata degli orari sotto ogni riga. Telefono, email, Facebook e Instagram hanno la stessa struttura, quindi non possono disallinearsi.
- **Facebook e Instagram diventano due righe** al posto del blocco "Social" con pillole: il valore è "Pagina del locale" / "Profilo del locale", perché i nomi reali delle pagine non sono ancora noti (nessun dato inventato).
- **Tutta la riga si tocca** (area di almeno 68 px di altezza); su computer la freccia si sposta di 3 px al passaggio del mouse, ferma con "riduci movimento". Le righe sono larghe al massimo 34rem come gli orari: su computer i contatti non si allargano più in tre colonne.
- **Alternative scartate**: tessere (più ingombranti su telefono), pillole in fila (perdono l'etichetta), biglietto centrato (contro l'allineamento a sinistra di tutta la lavagna), lista allineata (resta il blocco social diverso dagli altri).
- **Test**: nuovo `test_info_contatti_righe_intere`; 193 test superati; nessuno scorrimento orizzontale a 360 e 1366 px, icone tutte sulla stessa verticale.

## 2026-10-22 · Fase 2 – "Come arrivare" di nuovo nella fascia di Orari e contatti

- **Ripensamento di Ivan**: il pulsante nella fascia "Dove siamo" di `/info` torna, perché lì in fondo alla pagina è comodo. È superfluo solo nella home, dove "Come arrivare" è già nell'hero subito sopra (la home continua a svuotare il blocco `footer_come_arrivare`). Menù e Orari e contatti tengono il pulsante nella fascia.
- **Test**: `test_home_come_arrivare_una_volta` ora controlla che `/info` abbia `pulsante-footer`.

## 2026-10-22 · Fase 2 – Striscia chiara in fondo a Orari e contatti (e Menù) su telefono

- **Segnalazione di Ivan**: su `/info` da telefono, tornando in cima alla pagina, in fondo allo schermo ricompariva una striscia chiara (come quella già tolta dalla home). Lo sfondo di loghi è `position: fixed` grande quanto lo schermo "piccolo"; con la barra del browser galleggiante o che si nasconde, lo spazio sotto la barra restava crema senza loghi.
- **Rimedio**: lo sfondo scende del 20% dell'altezza dello schermo oltre il bordo inferiore (`inset: 0 0 -20vh`); le 16 file di loghi (1344 px) bastano a coprirlo. Vale anche per il Menù, che usa lo stesso sfondo. Da confermare da Ivan sul telefono.
- **Test**: 193 test superati (solo CSS).

## 2026-10-22 · Fase 2 – Fondo della pagina rosso quando si arriva al footer (Safari su iPhone)

- **Segnalazione di Ivan**: in home il fondo blu (messo per la striscia chiara sotto la barra di Safari) faceva comparire una riga blu sotto il footer rosso. Succede solo con Safari su iPhone: da iOS 26 colora lo spazio sotto la sua barra "a vetro" con il fondo della pagina e ignora `theme-color` (WebKit lo considera voluto).
- **Rimedio**: nuovo `static/js/fondo-pagina.js`, caricato da `base.html`. Un IntersectionObserver mette la classe `al-footer` su `<html>` quando il footer rosso entra nello schermo e la toglie quando esce; con la classe il fondo del `body` diventa rosso. In cima resta il colore di prima (blu in home, crema nelle altre pagine). Senza JavaScript tutto resta come prima.
- **Test**: aggiunto `test_fondo_rosso_al_footer`; 194 test superati. Provato in Chromium: fondo blu o crema in cima e rosso in fondo su home, Info e Menù. Su Safari va confermato da Ivan.
- **Correzione per Menù e Orari e contatti** (Ivan: in home funzionava, lì no): Safari prende il colore anche dagli elementi fissi che toccano il bordo dello schermo, e lo sfondo di loghi crema (fisso) copriva il rosso. Finché il footer è sullo schermo, `fondo-pagina.js` aggiorna `--taglio-sfondo` a ogni scroll e lo sfondo di loghi finisce dove comincia la fascia "Dove siamo", senza toccare il bordo in basso. A vista non cambia nulla, perché quella parte era già coperta dalle fasce del footer. Provato in Chromium: il bordo inferiore dello sfondo coincide con l'inizio della fascia.
- **"Browser" di Oppo (app "Internet" su Reno 12 Pro)**: su Info e Menù, in cima alla pagina, sotto la barra in basso resta una striscia crema senza loghi. Due tentativi, nessuno ha funzionato sul telefono di Ivan, quindi entrambi tolti: (1) file di loghi ferme anche sul fondo del `body`; (2) `viewport-fit=cover` più `env(safe-area-inset-*)` (dalla [guida edge-to-edge di Chrome](https://developer.chrome.com/docs/css-ui/edge-to-edge)). Ipotesi rimasta: quel browser riempie la zona sotto la sua barra con il solo colore di fondo della pagina (crema), e lì il sito non può disegnare. Restano attivi `fondo-pagina.js` e lo sfondo accorciato al footer, utili per Safari e per la home.

## 2026-10-22 · Fase 2 – Archivo come carattere del testo

- **Testo normale in Archivo al posto del carattere di sistema**: prima il testo usava `system-ui`, quindi cambiava da un dispositivo all'altro (Roboto su Android, San Francisco su iPhone, Segoe UI su Windows). Ora è uguale ovunque. Anton (titoli), Archivo Black (voci e prezzi) e Cabin Sketch (lavagna di Orari e contatti) restano come prima.
- **Perché Archivo**: è la versione normale della stessa famiglia di Archivo Black, già usata nel menù, quindi il sito resta un unico sistema coerente; si legge bene anche su descrizioni e numeri. Rosa di 5 valutata (Inter, Montserrat, DM Sans, Bricolage Grotesque, Archivo); su un'anteprima a confronto con Bricolage Grotesque e il carattere di sistema Ivan ha notato differenze minime e ha scelto Archivo.
- **Un solo file variabile** (`archivo-latin-variabile.woff2`, 36 KB, sottoinsieme latino, dal pacchetto npm `@fontsource-variable/archivo`) copre tutti i pesi usati, da 400 a 800, invece di un file per peso. Licenza SIL OFL in `OFL-Archivo.txt`, crediti in `docs/CREDITI_IMMAGINI.md`. `font-display: swap`: finché non è caricato si vede il carattere di sistema, che resta come riserva in `--font`.

## 2026-10-22 · Fase 2 – Titoli in Archivo largo e margini uguali a destra e a sinistra

- **Titoli in Archivo largo e nero al posto di Anton** (titoli delle pagine, insegna al neon, nastro, categorie del menù): su un'anteprima a tre (Anton, Archivo stretto, Archivo largo) Ivan ha scelto il largo. Archivo stretto era quasi uguale ad Anton; il largo cambia davvero il carattere del sito, lettere "schiacciate" come uno smash burger, e lascia una sola famiglia per testo e titoli. Anton tolto (file e licenza).
- **Un solo file variabile con due assi** (`archivo-latin-variabile.woff2`, 90 KB, peso 100–900 e larghezza 62–125%): `@font-face` con `font-stretch: 62% 125%`, titoli con `font-weight: 900` e `font-stretch: 125%`. Archivo Black resta per nomi delle voci e prezzi.
- **Grandezze ridotte di circa un quarto**, perché le lettere larghe occupano più spazio, e legate alla larghezza dello schermo dove una parola lunga non entrerebbe a 320 px: insegna `min(1.85rem, (100vw - 76px) / 13.3)`, categorie `min(2.25rem, 10.4vw)` ("ORIGINALS" è la parola più lunga), Burger `min(3.1rem, 13.6vw)`, titolo di Orari e contatti `min(1.5rem, (100vw - 60px) / 12.4)`. Senza questi limiti a 320 px "ORIGINALS" allargava tutta la colonna dei blocchi (pagina più larga dello schermo di 16 px).
- **Controllo dei margini** (richiesta di Ivan: stessi pixel dal bordo destro e dal sinistro), misurato con Playwright su 9 pagine (pubbliche e area proprietario) e 10 larghezze da 320 a 1920 px. Le scatole erano già centrate; erano storti i contenuti visibili:
  - **Navbar**: scritta a 16 px dal bordo sinistro, linee del pulsante a 21 px dal destro (telefono); su computer 28 px contro 34 px. Ora spazio interno uguale (`padding: 0 1rem` e `0 1.75rem`) e il pulsante a tre linee e l'ultima voce sporgono nel bordo di quanto è il loro spazio interno: 16/16 px e 28/28 px.
  - **Blocchi del menù, lavagna di Orari e contatti, blocchi dell'area proprietario**: l'ombra piena di 7 px a destra lasciava 12 px a sinistra e 5 px a destra. Ora `margin-right: 7px` (posto per l'ombra): 12/12 px a vista. Stessa cosa per la nota rossa del Burger (ombra di 3 px).
  - **Pillole dell'indice**: in fondo allo scorrimento l'ultima pillola finiva a 15 px dal bordo invece di 12: spazio finale ridotto a 3 px, quanto la sua ombra.
  - **Navbar tra 900 e 1100 px**: "Orari e contatti" andava a capo (il testo in Archivo è un po' più largo del carattere di sistema). Voci su una riga (`white-space: nowrap`) e un po' più vicine in quella fascia.
  - **Orari e contatti a 320 px**: le scritte "Indicazioni" e "WhatsApp" uscivano dai pulsanti e le ore della sera uscivano dalla lavagna (fino a 19 px). Sotto i 380 px lavagna con meno spazio interno e testo di pulsanti e orari più piccolo: ora tutto resta dentro. Ricontrollato su 90 combinazioni pagina × larghezza: nessuna pagina più larga dello schermo e nessun testo fuori dal suo riquadro.

## 2026-10-22 · Fase 2 – Regole di leggibilità e ombra di THE ORIGINALS

- **Ricerca sulle regole di un buon sito** (grandezze, lunghezza delle righe, interlinea, scala dei titoli, Core Web Vitals, contrasto): il confronto con il sito ha dato tre correzioni piccole.
  - **Nessun testo sotto i 12 px**: marchio "SmashBroski Pompei" nella navbar da 0,72 a 0,75rem; etichette sopra le colonne dei prezzi nel menù su computer da 0,68 a 0,75rem (ora tutte e quattro su tre righe uguali).
  - **Righe di circa 65 caratteri** nelle pagine di testo (Privacy): `max-width: 65ch` su paragrafi ed elenchi; prima arrivavano a circa 110 caratteri.
  - **Descrizioni del menù** con interlinea 1,5 invece di 1,4.
- **Errore trovato durante le prove**: nelle pagine brevi (Privacy, accesso, errori) il footer è subito sullo schermo, quindi `al-footer` rendeva rosso tutto il fondo e titoli e testo blu non si leggevano. Ora il `main` di quelle pagine (`main:has(> .pagina-testo)`) ha il suo fondo crema.
- **Ombra di THE ORIGINALS** (segnalazione di Ivan): il titolo BURGER aveva l'ombra piena blu scuro, THE ORIGINALS, anche lui su fondo chiaro, no. Stessa ombra di 4 px anche lì. Provato a 320, 390 e 1366 px: nessuno scroll orizzontale, il titolo resta nel blocco.

## 2026-10-23 · Fase 2 – Prezzi in colonna e simmetria di tutte le pagine

- **Prezzi degli Starters su una colonna** (segnalazione di Ivan): sul computer i bollini a prezzo unico (Patatine stick) stavano 7 px più a destra di 7,00 €. Ora vanno nell'ultima colonna, larghi quanto la colonna dei prezzi (6,3rem) e centrati come "10 PZ" e 7,00 €; il nome usa anche le colonne libere, così "Patatine stick bacon & cheese" resta su una riga.
- **Ricerca di altri difetti di simmetria** su tutte le pagine (pubbliche, accesso, errori, area proprietario), a 360 e 1366 px, misurati con Playwright:
  - **Bollini a prezzo unico** larghi quanto una colonna di prezzi anche in Kids, Soft drinks e Beers: cadono sulla stessa verticale della colonna destra degli Starters.
  - **Bollino centrato in verticale** su nome e descrizione (Kids menù), come i prezzi dei burger; prima stava sulla riga del nome e spingeva giù la descrizione. Senza descrizione nome e bollino sono centrati sulla stessa riga (bibite, patatine), anche su telefono.
  - **Starters e Salad**, sulla stessa riga, hanno la stessa altezza.
  - **Hero della home**: il testo cominciava 20 px più a sinistra di "Dove siamo"; ora la colonna dell'hero è larga quanto il testo del footer.
  - **Orari e contatti**: i pulsanti Chiama/Indicazioni/WhatsApp (36rem) sporgevano di 30 px oltre orari e contatti (34rem); ora tutti larghi 34rem.
  - **Privacy ed errori**: colonna di 900 px centrata ma righe di 65 caratteri, quindi testo tutto a sinistra; ora la colonna è larga quanto le righe (`calc(65ch + 2rem)`) e resta centrata. Accesso: colonna di 30rem, quanto i campi.
  - **Area proprietario**: l'indice non aveva spazio sotto la barra e il titolo era 8 px più a destra che nelle altre pagine dell'area; ora stesso spazio. Schede delle categorie staccate di 1,5rem (prima si toccavano). Tabelle con colonne di larghezza fissa: Prezzi, Stato e Azioni partono alla stessa x in tutte le categorie. "Annulla" staccato da "Salva".
- **Prove**: 194 test superati; nessuna pagina più larga dello schermo a 320, 768, 900, 1000 e 1366 px. Anteprime prima/dopo fuori da Git.

## 2026-10-23 · Fase 2 – Hero della home senza balzi quando si risale

- **Segnalazione di Ivan** (video dal telefono, browser "Internet" di Oppo): solo in home, risalendo verso l'alto, l'hero sembrava fare un balzo o ingrandirsi all'improvviso. Menù e Orari e contatti scorrevano normali.
- **Causa**: l'hero era alto `100dvh`. Mentre si scorre la barra dell'indirizzo si nasconde e ricompare, e con `dvh` l'altezza dell'hero cambiava ogni volta: la foto (`object-fit: cover`) si riadattava e la pagina si ridimensionava durante lo scroll. Le altre pagine non usano unità legate allo schermo per l'altezza. Esclusi scroll-snap e scroll fluido (non usati) e i due script del fondo, che cambiano solo colori e animazioni.
- **Rimedio**: `min-height: 100svh`, l'altezza dello schermo con la barra visibile, che non cambia durante lo scroll; `100vh` resta come riserva per i browser vecchi. Con la barra nascosta sotto l'hero si vede l'inizio di "Dove siamo", blu come il fondo dell'hero. Alternativa scartata: `100lvh`, che in cima farebbe finire i pulsanti sotto la barra del browser. La regola della skill di design "min-h-dvh invece di 100vh" serve a non avere un hero più alto dello schermo; `svh` lo rispetta e in più evita lo spostamento del contenuto (CLS).
- **Prove**: solo CSS. Confermato da Ivan sul suo telefono (browser Oppo): lo scroll della home non fa più balzi.

## 2026-10-23 · Fase 2 – Blocchi del menù dritti e spazi interni uguali

- **Blocchi dritti** (Ivan, sugli screenshot del menù: "piccole imprecisioni... sarebbe meglio allineare meglio le distanze"): Salad, Kids Menù e Beers erano ruotati di circa mezzo grado, gli altri no. Su elementi grandi i bordi di due blocchi vicini non erano paralleli e le righe tratteggiate pendevano: sembrava un errore, non una scelta. Tolte le tre rotazioni; l'aria "attaccata a mano" resta negli elementi piccoli (etichetta Menù, nastro, nota del Burger, bollini Winter/Summer Edition).
- **Stesso spazio sopra e sotto**: dal bordo al titolo 26 px, dall'ultima voce al bordo erano 46 px (37 nelle bibite). Ora l'ultima voce non ha spazio interno in basso né margini del testo: circa 26 px in tutti i blocchi.
- **Spazio in più diviso fra le voci**: Starters e The Originals sono allungati per pareggiare il blocco vicino, e tutto lo spazio in più finiva in fondo (62 e 110 px). Su computer i blocchi sono colonne flex e le voci crescono (`flex-grow: 1`): righe tratteggiate equidistanti e fondo pari al vicino. La nota "Ortaggio su base stagionale" resta larga quanto il testo (`align-self: flex-start`).
- **Prove**: 194 test superati; misurato con Playwright a 1366 px (spazio sopra il titolo 26 px, sotto l'ultima voce 23–26 px in tutti i blocchi). Anteprime prima/dopo fuori da Git.

## 2026-10-23 · Fase 2 – Scroll fluido su computer in Home e Orari e contatti

- **Segnalazione di Ivan**: su computer, scorrendo veloce, Home e Orari e contatti andavano a scatti; il Menù era fluido e sul telefono tutto andava bene.
- **Misura invece di ipotesi**: traccia di Chromium (Playwright, 1440×900) durante uno scroll veloce con la rotella, togliendo un elemento alla volta. Esclusi sfondo di loghi, insegna al neon, sfumature della lavagna e taglio dello sfondo al footer.
- **Orari e contatti, causa**: l'onda di "oggi" si muoveva animando `background-position`, quindi il browser ridisegnava la lavagna a ogni fotogramma, anche durante lo scroll (disegno 292 ms e rasterizzazione 753 ms nella prova, contro 30 e 49 del Menù). **Rimedio**: sul computer l'onda è un `::after` su un livello proprio che si sposta con `transform` di 24 px per ciclo, la stessa onda e lo stesso movimento (stessi pixel a parità di tempo). Dopo: 14 e 40 ms, come il Menù.
- **Home, causa**: quando arriva il footer il fondo della pagina passa da blu a rosso (per Safari su iPhone) e il browser ridisegnava tutta la foto dell'hero, proprio all'inizio dello scroll. **Rimedio**: sul computer `.hero { will-change: transform }`, l'hero sta su un livello suo e si ridisegna solo il fondo (rasterizzazione da 173 a 14 ms).
- **Solo computer** (`@media (hover: hover) and (pointer: fine)`): sul telefono era già fluido; controllato con l'emulazione di un Pixel 7 che gli stili calcolati siano identici a prima.
- **Non toccato**: il vetro sfocato della navbar in home quasi raddoppia il costo di composizione di ogni fotogramma, ma è una scelta grafica approvata. Ridurre la sfocatura non cambia la misura; se la home resta poco fluida si può togliere solo sul computer.
- **Prove**: solo CSS; misure prima/dopo con Playwright e confronto pixel dell'onda.

## 2026-10-24 · Fase 2 – Collaudo dell'area proprietario

- **Grafica chiusa, si passa al lato proprietario.** L'area esisteva dal 17/10 (RF-16–RF-19) ma dopo la grafica nessuno l'aveva più provata dall'inizio alla fine: prima di cambiarla, collaudo senza toccare il codice.
- **Test automatici**: 194 superati (MariaDB con lo schema adattato; da rilanciare su MySQL 8).
- **20 casi provati nel browser** (Playwright, 360×800 e 1366×768), tutti superati: accesso anonimo mandato al login; password sbagliata ed email inesistente con lo stesso messaggio; cookie di sessione HttpOnly e SameSite=Lax; `Cache-Control: no-store`; nessuno scroll orizzontale; nuova voce con prezzo "3.00" rifiutata con i campi ancora compilati, poi salvata con "3" e "5,00" e visibile subito nel menù; nome doppio nella categoria rifiutato; prezzo modificato, voce nascosta e rimostrata; avviso del cambio di categoria; turno 19:00–01:30 salvato e mostrato in Orari e contatti; martedì aperto e richiuso; sovrapposizione domenica–lunedì, inizio uguale alla fine e turno senza fine rifiutati; POST senza token CSRF rifiutato (400); al sesto login sbagliato in un minuto 429 "Troppi tentativi"; dopo "Esci" l'area non è più accessibile.
- **Difetti trovati, da correggere uno alla volta**: sul telefono il campo "alle" degli orari va a capo e spezza ogni turno; un turno con solo l'inizio riceve "scrivi le ore nel formato HH:MM" invece di "manca l'ora di fine"; nell'area ci sono due link "Menù" che portano a pagine diverse; l'elenco delle voci sul telefono è lungo circa 6900 px senza indice delle categorie; il blocco dopo 5 tentativi vale per l'IP e ferma anche la password giusta per un minuto, senza che il modulo lo dica.
- **Manca**: il cambio della password dall'area (oggi solo ricreando l'utente da riga di comando). Eliminare una voce e modificare contatti e logo restano fuori per scelta.
- **Da verificare sull'Oppo Reno 12 Pro**: campi dell'ora a 24 ore (Chromium senza interfaccia li mostra AM/PM) e un possibile lampo del pannello del menù mobile al caricamento.

## 2026-10-24 · Fase 2 – Orari dell'area proprietario su una riga per turno

- **Problema (dal collaudo)**: sul telefono "Dalle [campo] alle" stava su una riga e il secondo campo andava a capo da solo, quindi ogni turno occupava due righe spezzate e la pagina degli orari era lunga 3650 px a 360 px di larghezza.
- **Telefono**: "Dalle" e "alle" sopra il proprio campo (griglia di due colonne larghe al massimo 10rem, riempita per colonna), i due campi affiancati anche a 320 px. Etichette a 14 px nel colore secondario, sempre collegate al campo con `for`; campi alti 48 px. Pagina da 3650 a 2808 px.
- **Da 768 px**: "Dalle [ ] alle [ ]" su una riga (colonne `auto 10rem auto 10rem` addossate a sinistra), come si legge un orario. Pagina da 2512 a 2244 px a 1366 px.
- **Scartato**: togliere le etichette visibili e lasciare solo "[ ] – [ ]" con etichette per i lettori di schermo (più compatto, ma meno chiaro per il proprietario); campi uno sotto l'altro (pagina ancora più lunga).
- **Solo CSS** (`.riga-turno`), nessun template toccato. 194 test superati.

## 2026-10-24 · Fase 2 – Orari: messaggio chiaro quando manca un'ora

- **Problema (dal collaudo)**: un turno con solo l'ora di inizio riceveva "scrivi le ore nel formato HH:MM", ma il formato era giusto: mancava l'ora di fine.
- **Ora `valida_turni` distingue il campo vuoto dall'ora scritta male**: "Giovedì: manca l'ora di fine del turno (se chiude dopo mezzanotte, es. 01:00)." e "Mercoledì: manca l'ora di inizio del turno."; il messaggio sul formato HH:MM resta per le ore non valide. Il suggerimento sulla mezzanotte è nel messaggio perché è il caso in cui è più facile sbagliare.
- **Test**: `test_manca_ora_di_fine_messaggio_chiaro`, `test_manca_ora_di_inizio_messaggio_chiaro`. 196 test superati.

## 2026-10-24 · Fase 2 – Barra dell'area proprietario distinta dalla navbar

- **Problema (dal collaudo)**: nell'area c'erano due link "Menù": quello della navbar (menù pubblico) e quello della barra dell'area (gestione delle voci).
- **Voci della barra dell'area: "Gestisci il menù", "Gestisci gli orari", "Esci"**. La navbar resta com'è: dall'area si apre al volo la pagina pubblica per controllare una modifica. Scartato: togliere la navbar nell'area (si perde il controllo rapido) o rinominare le voci pubbliche.
- **Pagina corrente segnata** con `aria-current="page"` (anche in nuova voce e modifica, che fanno parte della gestione del menù): testo blu notte senza sottolineatura e riga rossa sotto, come una scheda selezionata.
- **Test**: `test_barra_area_distinta_dalla_navbar_e_pagina_corrente`. 197 test superati.

## 2026-10-24 · Fase 2 – Indice delle categorie in "Gestisci il menù"

- **Problema (dal collaudo)**: sul telefono l'elenco delle voci era lungo circa 6900 px e per arrivare a The Originals bisognava scorrere tutto.
- **Stesso indice a pillole del menù pubblico** (stesso markup, stessa classe `.indice`, stesso `static/js/indice.js`): fisso sotto la navbar, pillola rossa sulla categoria che si sta guardando, atterraggio preciso al tocco. Nessun CSS né JavaScript nuovo: le sezioni dell'area hanno già `section.categoria` con il titolo `h2` e l'id della categoria. Etichetta per i lettori di schermo "Categorie da gestire".
- **Verifica**: a 360 px un tocco su THE ORIGINALS porta il titolo a 188 px dall'alto con la pillola attiva; nessuno scroll orizzontale. Test `test_indice_categorie_nella_gestione_del_menu`. 198 test superati.

## 2026-10-24 · Fase 2 – Accesso: nota sul blocco dopo 5 tentativi

- **Problema (dal collaudo)**: dopo 5 login sbagliati in un minuto Flask-Limiter blocca l'indirizzo IP, quindi anche la password giusta riceve "Troppi tentativi" per un minuto, e il modulo non lo diceva.
- **Nota sotto "Entra"**: "Dopo 5 tentativi sbagliati l'accesso si blocca per un minuto, anche con la password giusta.", 14 px nel colore secondario, collegata al campo password con `aria-describedby` (i lettori di schermo la leggono con il campo). Scartato: mostrare i tentativi rimasti (rivelerebbe il funzionamento del limite a chi prova password a caso).
- **Test**: `test_login_avvisa_del_limite_di_tentativi` controlla anche che `LIMITE_TENTATIVI_LOGIN` sia ancora "5 per minute", così nota e limite non si separano. 199 test superati.
- **Chiusi i 5 punti deboli del collaudo del 24/10.** Resta il cambio della password dall'area.

## 2026-10-24 · Fase 2 – Cambio della password e comandi di gestione dell'account

- **Ruoli (deciso con Ivan)**: il proprietario gestisce dal sito solo i contenuti (voci, prezzi, orari) e la propria password; lo sviluppatore gestisce account, password dimenticate, blocchi, database e server, solo da riga di comando. Principio del minimo privilegio: nel sito non c'è nessuna pagina di amministrazione da attaccare.
- **Nessun blocco permanente dopo N errori** (OWASP, Authentication Cheat Sheet): chiunque conosca l'email potrebbe chiudere fuori il proprietario apposta. Resta il limite temporaneo di 5 tentativi al minuto per connessione, che con password di almeno 12 caratteri e Argon2id basta contro chi prova password a caso.
- **Pagina "Cambia password"** (`/proprietario/password`, voce nella barra dell'area): password attuale, nuova e conferma. `AuthService.cambia_password` verifica l'attuale con Argon2id (così chi trova il telefono con la sessione aperta non può cambiarla), poi controlla almeno 12 caratteri, conferma uguale e nuova diversa dall'attuale; errori raccolti tutti insieme. Le password scritte non tornano mai nella pagina. Dopo il cambio la sessione viene svuotata e ricreata. Campi con `autocomplete="current-password"` / `"new-password"` per i gestori di password.
- **Stesso limite del login sul cambio password** (5 POST sbagliati al minuto, poi 429): con la sessione aperta non si può provare la password attuale all'infinito. Contano tutti i tentativi rifiutati, anche per conferma diversa: con 5 al minuto non ostacola un uso normale.
- **Comandi nuovi**: `flask --app app reimposta-password` (email e nuova password nascosta e ripetuta, senza quella attuale), `disattiva-proprietario EMAIL` e `riattiva-proprietario EMAIL` (colonna `attivo`, già controllata dal `before_request`: chi è dentro esce alla richiesta successiva). Nuovo metodo `UtenteRepository.aggiorna_attivo`.
- **Limite noto**: le sessioni sono cookie firmati, quindi cambiare la password non chiude le sessioni aperte su altri dispositivi (scadono in 8 ore). Per chiuderle subito: disattivare l'account o cambiare la `SECRET_KEY`. Scartato per ora un contatore di versione della sessione nel database (una colonna e un controllo in più per un solo account).
- **`docs/GESTIONE_SITO.md`**: tutti i comandi dello sviluppatore (ambiente, avvio anche dal telefono, test, account, database, immagini, Git) e cosa fare se l'account sembra compromesso. `PROGETTAZIONE.md` aggiornata (RF-16, `AuthService`, rotte, `comandi.py`).
- **Test**: 14 nuovi (8 in `test_auth_service.py`, 5 in `test_area_proprietario.py` tra pagina e comandi, limite dei tentativi in `test_accessi.py`; la nuova rotta è anche nel controllo CSRF). 213 test superati.


## 2026-10-24 · Fase 2 – Analisi di sicurezza e correzioni prima della pubblicazione

- **Analisi** del repository pubblico e del codice: storia Git completa (nessun `.env`, password o chiave; commit con l'email noreply di GitHub), `pip-audit` sulle versioni di `requirements.txt` (nessuna vulnerabilità nota al 24/10), `bandit`, query SQL, escape dei template, CSRF, password, sessioni, header. Codice solido; i punti deboli riguardano la messa online.
- **Email reale negli esempi**: due docstring di `app/comandi.py` usavano l'email dell'account di sviluppo. Sostituita con `proprietario@example.com`; resta nella storia Git, quindi online l'account del proprietario si crea con un'altra email.
- **`docs/GESTIONE_SITO.md` resta nel repository**: i comandi non sono segreti (principio di Kerckhoffs), funzionano solo per chi ha già accesso al server. Aggiunte le sezioni "Pubblicazione online" (checklist) e "Cosa può stare nel repository pubblico".
- **Dimensione delle richieste**: `MAX_CONTENT_LENGTH` 64 KB (413 "Dati inviati troppo grandi."). **Password al massimo 128 caratteri** (creazione, reimpostazione, cambio; al login una password più lunga è rifiutata senza calcolare l'hash), `maxlength="128"` nei campi.
- **ProxyFix** con `PROXY_FIDATI` in `.env` (0 in sviluppo): dietro il proxy dell'hosting il limite dei tentativi conta l'IP del visitatore invece di quello del proxy, che bloccherebbe il login a tutti.
- **Header nuovi**: `Permissions-Policy` (fotocamera, microfono, posizione, pagamenti, USB negati) e `Cross-Origin-Opener-Policy: same-origin`.
- **`run.py`** si rifiuta di partire con `PRODUZIONE=1` (il debugger online permetterebbe di eseguire codice).
- **Test**: 5 nuovi (password troppo lunga e di 128 caratteri, richiesta troppo grande, IP con e senza proxy) e controllo dei nuovi header. 218 test superati.

## 2026-10-24 · Fase 2 – Il cambio della password chiude le altre sessioni

- **Problema**: le sessioni sono cookie firmati, quindi dopo un cambio di password una sessione rubata o dimenticata su un altro dispositivo restava valida fino a 8 ore. Ivan preferisce che si esca subito.
- **Impronta della password nella sessione** (`app/sessione.py`): al login la sessione riceve, oltre all'id, un HMAC-SHA256 dell'hash Argon2 calcolato con la `SECRET_KEY` (il cookie è leggibile, l'hash non deve finirci). Il `before_request` dell'area lo confronta con l'hash attuale (`hmac.compare_digest`): se la password è cambiata, la sessione si svuota e si torna al login. Nessuna colonna nuova nel database.
- **Chi cambia la password dall'area resta dentro**: la sua sessione viene ricreata con l'impronta nuova. Anche `reimposta-password` chiude tutte le sessioni. Effetto collaterale accettato: se un giorno Argon2 ricalcola l'hash con parametri nuovi al login, gli altri dispositivi escono una volta.
- **All'aggiornamento** le sessioni aperte prima (senza impronta) non valgono più: si rientra una volta.
- **Test**: la fixture `client_proprietario` entra dal login vero; 3 nuovi (sessione con il solo id rifiutata, cambio password che chiude l'altro dispositivo e tiene dentro chi la cambia, `reimposta-password` che chiude la sessione). 221 test superati.

## 2026-10-24 · Fase 2 – Password e sessioni allineate a OWASP e NIST

- **Ricerca** (fonti nel report di sicurezza dell'archivio, sezione 6): OWASP ASVS capitolo 3 (sessioni: chiusura al logout e al cambio password, timeout per inattività, durata massima), OWASP Web Security Testing Guide "Testing Session Timeout" (timeout lato server; 15 minuti per una banca, circa 60 per siti a basso rischio), NIST SP 800-63B rev. 4 (minimo 15 caratteri se la password è l'unico fattore, almeno 64 ammessi, niente regole di composizione né cambi periodici, confronto con un elenco di password note obbligatorio, limite ai tentativi), discussione OWASP ASVS #906 sui limiti di tentativi. Già in regola: chiusura delle sessioni al cambio password, password attuale richiesta, niente regole di composizione, 128 caratteri ammessi, limite di tentativi, logout lato server.
- **Password minima 15 caratteri** (prima 12, il minimo di OWASP ASVS). Le password già in uso più corte restano valide: il controllo vale quando se ne sceglie una nuova.
- **Password facili da indovinare rifiutate** in creazione, reimpostazione e cambio: elenco `app/dati/password_comuni.txt` (11.143 password di 15-128 caratteri da due elenchi di SecLists, licenza MIT; si rigenera con `strumenti/elenco_password_comuni.py`), meno di 5 caratteri diversi, nome del sito ("smashbroski") o parte dell'email prima della @, ignorando maiuscole, spazi e segni. Nessun servizio esterno (scartato Have I Been Pwned: un'altra dipendenza di rete per un solo account). Testo della pagina Cambia password aggiornato.
- **Correzione di un errore dell'analisi precedente**: con `session.permanent` Flask rinnova il cookie a ogni richiesta, quindi le "8 ore" erano 8 ore di inattività e la sessione di chi usa l'area ogni giorno non scadeva mai. Ora `app/sessione.py` salva nella sessione firmata l'ora del login e dell'ultima attività e il `before_request` chiude la sessione dopo **1 ora di inattività** o **8 ore dal login**, con il messaggio "Sessione scaduta" nella pagina di accesso.
- **Test**: 11 nuovi (password facili rifiutate in 6 casi su tre operazioni, frase di parole accettata, elenco caricato, 15 caratteri al limite, scadenza per inattività e per durata massima, attività che rinnova il timeout). 232 test superati.

## 2026-10-24 · Fase 2 – Prova del menù con molte voci

- **Domanda di Ivan**: la grafica del menù regge se il proprietario aggiunge panini, bibite e altro?
- **Prova** (archivio `docs/collaudi/menu-pieno/`, con gli script): voci aggiunte con `MenuService.crea_voce`, lo stesso percorso dei moduli dell'area. Realistica: +17 voci (42 in tutto: Burger +5 con 2 o 4 formati, Soft Drinks +4, Starters +2, Beers +3, una in Salad, Kids e The Originals). Estrema: nome di 100 caratteri, descrizione di 255, edizione di 30, nota lunga, parola di 60 lettere senza spazi. Foto a 360, 768 e 1280 px e controllo automatico degli elementi oltre lo schermo.
- **Esito**: nessuno scroll orizzontale, nessun testo fuori dai blocchi, prezzi sempre in colonna, testi lunghi a capo. Sul telefono la pagina passa da circa 6.100 a 8.500 px: l'indice a pillole porta alle categorie.
- **Difetto corretto (da 900 px)**: The Originals è allungato per pareggiare la colonna accanto e le sue voci hanno `flex-grow: 1`; la voce è una griglia e lo spazio in più si divideva fra le righe interne, staccando la descrizione dal nome. Aggiunto `align-content: center` a `.colonne-2 .voce, .colonne-4 .voce`: la voce resta compatta e lo spazio va sopra e sotto, righe tratteggiate sempre equidistanti. Con 42 voci lo spazio fra nome e descrizione in Scarulella Bro passa da 29 px a 2 px (misurato nel browser); con le voci estreme lo stacco era più ampio.
- **Limite che resta**: con molte più voci a sinistra, The Originals ha voci molto distanziate (è alto quanto la colonna accanto); se un giorno disturba si smette di pareggiare le altezze. 232 test superati.

## 2026-10-24 · Fase 2 – Manuale del proprietario

- **`docs/MANUALE_PROPRIETARIO.md`**: istruzioni per il titolare, senza termini tecnici: entrare (indirizzo `/auth/login`, blocco dopo 5 tentativi, uscita dopo 1 ora di inattività o 8 ore), voci del menù (campi, prezzi con la virgola, formati, spostamento di categoria, nascondere e mostrare), orari (turni dopo mezzanotte, giorni di chiusura), password (regole e consigli), cosa chiedere allo sviluppatore, domande frequenti con i messaggi esatti del sito.
- **Nel repository** perché descrive il comportamento del codice e deve cambiare insieme a lui; non contiene dati reali. Indirizzo del sito, email dell'account e prima password vanno in una scheda di consegna separata, fuori da Git.

## 2026-10-24 · Fase 2 – Tentativi di accesso contati nel database

- **Problema**: Flask-Limiter contava i tentativi sbagliati nella memoria di ogni processo (`memory://`). Gli hosting Python fanno girare il sito su più processi (PythonAnywhere Developer ne ha 3), e ognuno aveva i suoi 5 tentativi. Prova con gunicorn a 3 processi e una sessione nuova a ogni richiesta: 14 tentativi sbagliati accettati su 18 in pochi secondi. In più, un riavvio azzerava il blocco.
- **Scelta**: tabella `tentativi_accesso` in MySQL, `TentativiRepository` (solo SQL), `TentativiService` (regole) e decoratore `limita_tentativi(ambito)` in `app/limiti.py` sulle rotte di login e cambio password, al posto di `@limiter.limit`. Stesse regole di prima: 5 tentativi sbagliati al minuto per IP e per ambito, poi 429; si contano solo le risposte 400 e chi entra al primo colpo non consuma il limite. Finestra scorrevole di 60 secondi (Flask-Limiter usava una finestra fissa al minuto): il blocco dura al massimo un minuto dal primo dei 5 errori. Le richieste rifiutate con 429 non si registrano, così il blocco non si allunga.
- **Privacy**: l'IP non si salva. Si salva un HMAC-SHA256 dell'IP con la `SECRET_KEY`, che basta per contare e non si può ricondurre all'indirizzo senza la chiave. Le righe più vecchie di un'ora si cancellano a ogni nuovo tentativo, quindi la tabella resta minuscola.
- **Flask-Limiter tolto** da `requirements.txt`: serviva solo a questo. Scartati: un solo processo (vincola l'hosting e un riavvio sblocca comunque), Redis (un servizio in più da pagare e mantenere per un solo modulo di login), Flask-Limiter con un altro archivio (la sua libreria `limits` non supporta MySQL).
- **Limite noto**: due richieste sbagliate che arrivano nello stesso istante possono leggere entrambe 4 e passare tutte e due (al massimo una o due in più, solo con richieste in parallelo). Flask-Limiter aveva lo stesso margine. Bloccarlo del tutto richiederebbe un lock di MySQL per ogni login, ed è troppo per un sito con un solo account.
- **Database esistenti**: `database/aggiornamenti/2026-10-24_tentativi_accesso.sql` crea solo la tabella nuova, senza ricaricare dati e account; `schema.sql` la crea nei database nuovi.
- **Test**: 8 nuovi (6 in `test_tentativi_service.py` con l'istante passato come parametro: soglia, fine del blocco al secondo 61, ambiti e IP separati, IP mai in chiaro, pulizia; 2 in `test_accessi.py`: login riusciti che non contano, limite condiviso fra due app come fra due processi). I test del limite usano `database_modificato`, perché i tentativi si confermano davvero. Prova con gunicorn a 3 processi: 5 risposte 400, poi solo 429, e 5 righe nella tabella. 240 test superati.

## 2026-10-25 · Fase 2 – Contatore dei tentativi rimasti

- **Richiesta di Ivan**: mostrare i tentativi rimasti (5, 4, 3…) così il proprietario si accorge prima del blocco. Ivan ha notato anche che il blocco compariva solo al sesto tentativo: i 5 errori erano già stati fatti, ma la pagina lo diceva solo alla richiesta successiva.
- **Decisione rivista**: il 24/10 il contatore era stato scartato perché avrebbe aiutato chi prova password. Il rischio è quasi nullo: la nota sotto "Entra" dice già il limite, il conteggio è per IP e non per account, scende allo stesso modo con email esistenti e inesistenti (nessuna enumerazione), e chi cambia IP riparte comunque da 5. Il vantaggio per il proprietario è concreto.
- **Messaggi** (`messaggio_tentativi_rimasti` in `app/servizi/tentativi.py`), dopo "Email o password non corretti.": "Tentativi rimasti: 4 su 5." fino a 2, poi "Ultimo tentativo: se sbagli ancora, l'accesso si blocca per un minuto.", al quinto errore "Hai sbagliato 5 volte: l'accesso è bloccato per un minuto, anche con la password giusta." Dal sesto la pagina 429 come prima. Stesse frasi nella pagina Cambia password, nell'elenco degli errori.
- **Come**: `TentativiService.rimasti()`; il decoratore `limita_tentativi` mette in `g.tentativi_rimasti` quanti ne resteranno se questo tentativo è sbagliato e registra il tentativo solo quando la rotta mette `g.password_sbagliata = True` (prima contava ogni risposta 400).
- **Correzione collegata**: nel cambio password conta solo la password attuale sbagliata. Prima anche una conferma diversa o una nuova password troppo corta consumavano un tentativo, e con il contatore visibile il proprietario si sarebbe visto scalare i tentativi senza aver sbagliato la password.
- **Test**: 5 nuovi (contatore al login con email esistente e inesistente, nessun contatore con il limite spento, cambio password che conta solo la password attuale, `rimasti()` da 5 a 0, frasi del contatore). 245 test superati nel cloud su MariaDB. Screenshot a 360 e 1366 px nell'archivio (`docs/collaudi/contatore-tentativi/`).
- **Notato durante le foto**: sul telefono, appena caricata una pagina, il pannello del menù della navbar si vede aperto per circa 300 ms e poi sparisce (misurato nel browser: opacità 1 al caricamento, 0 dopo 300 ms). È il "lampo del pannello" da verificare sull'Oppo: da correggere a parte.

