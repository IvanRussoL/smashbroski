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
- **Menù su desktop in colonne con l'intestazione dei formati (solo visiva, `aria-hidden`)**: griglia CSS con una colonna per formato, posizione presa dalla classe `colonna-<posizione del formato>` (gli stili in linea sono vietati dalla CSP); i `<dt>` restano nell'HTML per i lettori di schermo; formato mancante (Los Pollos double) con "—". Su telefono resta la lista formato-prezzo. Un prezzo unico in una categoria con formati (Patatine stick) va sotto il nome, non sotto una colonna, per non sembrare il prezzo di "10 pz".
- **Verifica con screenshot in tutti i viewport del piano** (360×800, 375×667, 390×600, 667×375, 844×390, 768×1024, 1366×768, zoom 200%): nessuno scroll orizzontale, nessuna sovrapposizione; logo, titolo, stato di apertura e pulsanti visibili nella prima schermata in tutti i casi, anche in orizzontale.
