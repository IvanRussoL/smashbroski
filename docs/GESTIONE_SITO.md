# Gestione del sito – comandi per lo sviluppatore

Tutto quello che si fa da riga di comando per installare, avviare, verificare e amministrare il sito. Il proprietario del locale gestisce dal sito solo voci, prezzi e orari e la propria password; account, database e server li gestisce lo sviluppatore da qui, mai da una pagina del sito.

I comandi sono per Windows (PowerShell, terminale di VS Code), da eseguire nella cartella del progetto (`smashbroski`) con l'ambiente virtuale attivo. Su Linux e macOS cambia solo l'attivazione dell'ambiente (`source venv/bin/activate`).

## 1. Ambiente

| Cosa | Comando |
|---|---|
| Creare l'ambiente virtuale (una volta) | `python -m venv venv` |
| Attivarlo (ogni volta che si apre il terminale) | `.\venv\Scripts\Activate.ps1` |
| Installare le librerie | `pip install -r requirements.txt` |
| Generare la `SECRET_KEY` per `.env` | `python -c "import secrets; print(secrets.token_hex(32))"` |

Il file `.env` (mai in Git) si crea copiando `.env.example` e contiene la password dell'utente MySQL dell'app e la `SECRET_KEY`.

## 2. Avviare il sito

| Cosa | Comando |
|---|---|
| Sito sul computer (http://127.0.0.1:5000) | `python run.py` |
| Sito visibile dal telefono sulla stessa rete Wi-Fi | `flask --app run run --host 0.0.0.0`, poi sul telefono http://IP-DEL-PC:5000 |
| Trovare l'IP del PC | `ipconfig` (voce "Indirizzo IPv4" della scheda Wi-Fi) |
| Elenco delle pagine e degli indirizzi | `flask --app run routes` |

`python run.py` ha il debug attivo: non usarlo per la rete. Per la prova dal telefono il firewall di Windows va aperto solo per le reti private. L'area proprietario si apre da `/auth/login`: nel sito non c'è nessun link, per scelta.

## 3. Test

| Cosa | Comando |
|---|---|
| Tutti i test | `python -m pytest` |
| Un solo file | `python -m pytest tests/test_area_proprietario.py` |
| Un solo test, con i dettagli | `python -m pytest -k cambia_password -v` |

I test usano il database `smashbroski_test` (`DB_NAME_TEST` in `.env`) e lo ricreano a ogni esecuzione: non toccano mai il database del sito.

## 4. Account del proprietario

| Cosa | Comando |
|---|---|
| Creare l'account (chiede email e password, che non compare a schermo) | `flask --app app crea-proprietario` |
| Nuova password se il proprietario l'ha dimenticata | `flask --app app reimposta-password` |
| Bloccare un account (non entra più; chi è dentro esce alla richiesta successiva) | `flask --app app disattiva-proprietario EMAIL` |
| Sbloccarlo | `flask --app app riattiva-proprietario EMAIL` |
| Vedere gli account (in MySQL Workbench) | `SELECT id, email, attivo, creato_il FROM utenti;` |

Regole:
- La password ha almeno 12 caratteri. Quella scelta con `crea-proprietario` o `reimposta-password` si comunica al proprietario a voce o di persona, mai per email, e gli si chiede di cambiarla subito da **Cambia password** nell'area: da quel momento la conosce solo lui.
- Dopo 5 tentativi sbagliati in un minuto (accesso o cambio password) quella connessione è bloccata per un minuto, poi si riprova. Non serve sbloccare niente. In sviluppo il conteggio è in memoria: riavviare il server lo azzera.
- Non esiste un blocco permanente dopo N errori, per scelta: chi conosce l'email potrebbe chiudere fuori il proprietario apposta.

### Se l'account sembra compromesso

1. `flask --app app disattiva-proprietario EMAIL`: esce subito da tutti i dispositivi.
2. `flask --app app reimposta-password` con una password nuova.
3. Se si vuole chiudere ogni sessione aperta di chiunque: nuova `SECRET_KEY` in `.env` e riavvio del sito (i cookie di sessione firmati con la vecchia chiave non valgono più).
4. `flask --app app riattiva-proprietario EMAIL` e consegna della nuova password.

Cambiare la password dall'area rinnova la sessione di chi la cambia, ma le sessioni aperte su altri dispositivi restano valide fino alla scadenza (8 ore): per chiuderle subito servono i passi 1 o 3.

## 5. Database

| Cosa | Come |
|---|---|
| Ricaricare tabelle e dati iniziali (cancella tutto, account compresi) | In MySQL Workbench, sul database `smashbroski`: eseguire `database/schema.sql`, poi `database/dati_iniziali.sql`; oppure da terminale `mysql -u root -p smashbroski -e "source database/schema.sql"` e lo stesso con `dati_iniziali.sql` |
| Dopo la ricarica | `flask --app app crea-proprietario` |
| Copia di sicurezza prima di cambiare i dati | `mysqldump -u root -p smashbroski > copia_smashbroski.sql` (in PowerShell: `cmd /c "mysqldump -u root -p smashbroski > copia_smashbroski.sql"`) |

L'utente MySQL dell'app (`smashbroski_app`) ha solo SELECT, INSERT, UPDATE e DELETE sul database del sito: le operazioni sulle tabelle si fanno come `root`.

## 6. Immagini

| Cosa | Comando |
|---|---|
| Convertire e ridimensionare le foto in WebP per il sito | `python strumenti/prepara_immagini.py CARTELLA_CON_GLI_ORIGINALI` |

Gli originali restano fuori da Git; nel sito vanno solo i WebP prodotti dallo script. Crediti delle immagini in `docs/CREDITI_IMMAGINI.md`.

## 7. Git

| Cosa | Comando |
|---|---|
| Scaricare il branch di lavoro | `git fetch origin` e `git switch pagina-info-variante-c` |
| Aggiornare il branch | `git pull` |
| `git status` segna `DEVLOG.md` o `stile.css` modificati ma il contenuto è uguale (solo fine riga di Windows) | `git restore DEVLOG.md app/static/css/stile.css` |
| Controllare che cambino solo le fini riga | `git diff --ignore-cr-at-eol --stat` (vuoto = solo fine riga) |

## 8. Pubblicazione online

Da controllare uno per uno prima di aprire il sito al pubblico:

1. **Account nuovo**: `flask --app app crea-proprietario` sul database online con un'email che non compare nel repository e una password nuova (mai quella usata in sviluppo).
2. **`.env` del server**: `SECRET_KEY` nuova, `PRODUZIONE=1` (cookie solo HTTPS e header HSTS), `PROXY_FIDATI` uguale al numero di proxy dell'hosting davanti al sito (di solito 1: si legge nella documentazione dell'hosting).
3. **Server WSGI, mai `python run.py`** (il debugger permette di eseguire codice dal browser; con `PRODUZIONE=1` `run.py` si rifiuta di partire). Su Windows `pip install waitress` e `waitress-serve --port=8000 run:app`, su Linux `pip install gunicorn` e `gunicorn --workers 1 run:app`. **Un solo processo**: il conteggio dei tentativi di login è nella memoria del processo, con più processi il limite si moltiplica (per averne di più serve Redis).
4. **HTTPS attivo** prima di aprire il login.
5. **Librerie senza vulnerabilità note**: `pip install pip-audit`, poi `pip-audit -r requirements.txt` (da ripetere ogni tanto anche dopo la pubblicazione, e aggiornare `requirements.txt` se segnala qualcosa).

## 9. Cosa può stare nel repository pubblico

Sì: codice, questo file, `.env.example`, indirizzo del login. La sicurezza non dipende dal fatto che nessuno sappia come funziona il sito, ma da password, Argon2, limite di tentativi e CSRF; i comandi di questo file funzionano solo per chi ha già accesso al server.

Mai: `.env`, password, `SECRET_KEY`, email reali degli account (neanche come esempio nei commenti), IP e dati dell'hosting, copie del database. Controllo prima di un push: `git diff --cached` e, per tutta la storia, `git log -p --all | Select-String "password|secret|@"` (PowerShell).

Se un segreto finisce in un commit già pubblicato, cancellarlo dal file non basta (resta nella storia): si cambia il segreto (nuova password, nuova `SECRET_KEY`, altro account).
