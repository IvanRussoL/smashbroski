# Manuale dell'area riservata

Istruzioni per il proprietario del locale: come entrare nel sito e aggiornare menù, prezzi, orari e password. Non serve nessuna conoscenza tecnica: bastano il telefono o il computer e un browser (Chrome, Safari, Firefox, Edge).

L'indirizzo del sito, l'email dell'account e la prima password vengono consegnati a parte, di persona: non sono scritti qui.

## 1. Entrare

1. Apri l'indirizzo del sito seguito da `/auth/login` (es. `www.sito-del-locale.it/auth/login`). Nel sito non c'è un pulsante per l'area riservata, per scelta: conviene salvare la pagina tra i preferiti.
2. Scrivi email e password e premi **Entra**.
3. Se email o password sono sbagliate compare "Email o password non corretti." (il sito non dice quale delle due, per sicurezza).

**Blocco dopo 5 tentativi**: dopo 5 tentativi sbagliati in un minuto l'accesso si blocca per un minuto, anche con la password giusta. Dopo ogni errore il sito dice quanti tentativi restano ("Tentativi rimasti: 3 su 5.", poi "Ultimo tentativo"); al quinto errore dice subito che l'accesso è bloccato. Basta aspettare un minuto e riprovare: non serve chiamare nessuno. Vale anche per la password attuale nella pagina Cambia password.

**Uscita automatica**: dopo **un'ora** senza aprire pagine dell'area, oppure **8 ore** dopo l'accesso, il sito chiede di entrare di nuovo ("Sessione scaduta"). Le modifiche già salvate restano; quelle scritte e non salvate vanno riscritte.

In alto nell'area ci sono quattro voci:

| Voce | A cosa serve |
|---|---|
| **Gestisci il menù** | Aggiungere, modificare, nascondere le voci e cambiarne i prezzi |
| **Gestisci gli orari** | Orari di apertura della settimana |
| **Cambia password** | Scegliere una password nuova |
| **Esci** | Uscire dall'area (da fare sempre su un computer non tuo) |

Le voci **Menù** e **Orari e contatti** della barra rossa in alto aprono le pagine che vedono i clienti: servono per controllare subito una modifica.

## 2. Il menù

La pagina **Gestisci il menù** mostra tutte le categorie (Starters, Salad, Burger, Kids Menù, Soft Drinks, Beers, The Originals) con le loro voci, anche quelle nascoste. Le pillole in alto portano subito alla categoria.

### Aggiungere una voce

1. Nella categoria giusta premi **Aggiungi una voce in …**.
2. Compila i campi:

| Campo | Obbligatorio | Esempio | Note |
|---|---|---|---|
| Nome | Sì | Smash Pompei | Massimo 100 caratteri. Due voci della stessa categoria non possono avere lo stesso nome |
| Ingredienti o descrizione | No | Bun, hamburger, provola, friarielli | Massimo 255 caratteri |
| Etichetta | No | Winter Edition | Compare in un bollino rosso accanto al nome. Massimo 30 caratteri |
| Nota | No | Prova anche la variante con la zucca | Compare in corsivo sotto la descrizione |
| Posizione | No | 3 | Ordine nella categoria; vuoto = in fondo |
| Prezzi | Sì | 7,50 | Vedi sotto |

3. Premi **Salva**. La voce compare subito nel menù pubblico.

**Prezzi**:
- Si scrivono **con la virgola**: `7`, `7,5` e `7,50` vanno bene; `7.50` con il punto no.
- Da 0,01 € a 999,99 €.
- Nelle categorie con più formati (es. Burger: panino single, panino double, menù single, menù double; Starters: 5 pz e 10 pz) si compilano solo i formati offerti e si lasciano vuoti gli altri: nel menù al loro posto compare un trattino.
- In alternativa si compila solo il **Prezzo unico** (es. bibite e birre). Non entrambi.

Se qualcosa non va, il sito non salva, scrive in rosso cosa correggere e tiene i dati già scritti.

### Modificare una voce

Premi **Modifica** accanto alla voce, cambia quello che serve e premi **Salva**. **Annulla** torna all'elenco senza salvare.

### Spostare una voce in un'altra categoria

1. Nella pagina di modifica scegli la nuova categoria dall'elenco **Categoria** e premi **Cambia categoria**.
2. Compaiono i formati di prezzo della nuova categoria: scrivi di nuovo i prezzi (quelli vecchi non valgono nella nuova categoria).
3. Premi **Salva**. Finché non salvi, la voce resta dov'era.

### Nascondere e mostrare

- **Nascondi** toglie la voce dal menù pubblico senza cancellarla (es. un panino finito o stagionale). Nell'elenco resta, segnata "Nascosta".
- **Mostra** la rimette nel menù con tutti i suoi dati.
- Una categoria con tutte le voci nascoste non compare nel menù pubblico.
- Le voci non si cancellano mai: si nascondono. Così una voce stagionale si ritrova l'anno dopo.

## 3. Gli orari

La pagina **Gestisci gli orari** ha un riquadro per ogni giorno con uno o più turni **Dalle … alle …**.

- Un turno appartiene al giorno in cui **inizia**. Se il locale chiude dopo la mezzanotte, l'ora di fine si scrive così com'è: lunedì **dalle 18:00 alle 01:00**.
- Pranzo e cena nello stesso giorno: due righe (es. 12:00–15:00 e 19:00–23:30). C'è sempre una riga libera in più.
- **Giorno di chiusura**: lascia vuote tutte le righe di quel giorno.
- Premi **Salva gli orari**. La pagina Orari e contatti e la scritta "Aperto ora / Chiuso" si aggiornano subito.

Il sito rifiuta turni che si accavallano (anche tra domenica notte e lunedì) e righe con una sola ora, e scrive quale giorno correggere.

## 4. La password

**Cambiarla** (consigliato al primo accesso, perché la prima password l'ha scelta lo sviluppatore):

1. **Cambia password**.
2. Scrivi la password attuale, la nuova e ripeti la nuova.
3. Premi **Cambia password**.

Regole della nuova password:
- da **15 a 128 caratteri**: la cosa più semplice è una **frase di tre o quattro parole** (es. "gatto lampione mercoledì"), facile da ricordare e difficile da indovinare;
- non può essere una password molto comune, ripetitiva (es. "aaaaaaaaaaaaaaa"), contenere il nome del locale ("smashbroski") o il nome dell'email;
- non servono maiuscole o simboli obbligatori, e non va cambiata a scadenza.

Dopo il cambio resti dentro; **tutti gli altri dispositivi** su cui eri entrato escono subito. Utile se hai lasciato l'area aperta sul computer del locale.

Consigli:
- non scriverla su un foglio vicino alla cassa e non mandarla per messaggio o email;
- puoi farla ricordare al browser o a un gestore di password;
- se pensi che qualcuno la conosca, cambiala subito.

## 4 bis. La verifica in due passaggi (consigliata)

Con la verifica in due passaggi, per entrare servono la password **e** un codice di 6 cifre che un'app del telefono cambia ogni 30 secondi. Anche chi scoprisse la password non entra senza il tuo telefono.

**Attivarla** (una volta sola, 2 minuti):

1. Sul telefono installa **Google Authenticator** (o Microsoft Authenticator) dallo store.
2. Nell'area apri **Verifica in due passaggi** e premi **Attiva la verifica in due passaggi**.
3. Nell'app tocca **+** → **Scansiona un codice QR** e inquadra il codice sullo schermo. Se sei già sul telefono e non puoi inquadrarlo, scegli "Inserisci una chiave di configurazione" e scrivi la chiave mostrata sotto il QR.
4. Scrivi nel sito il numero di 6 cifre che compare nell'app sotto "SmashBroski Pompei" e premi **Attiva**.
5. Compaiono **10 codici di riserva**: scrivili su un foglio o fotografali e conservali **fuori dal telefono**. Non li vedrai più.

**Entrare** con la verifica attiva: email e password come sempre, poi la pagina **Codice di verifica**: apri l'app e scrivi il numero di 6 cifre (entro 5 minuti dalla password). Anche qui dopo 5 codici sbagliati si aspetta un minuto.

**Senza telefono**: al posto del numero scrivi uno dei codici di riserva (es. `abcde-fghjk`); ognuno vale una volta. Quando ne restano 3 o meno il sito lo ricorda: da **Verifica in due passaggi** puoi crearne 10 nuovi (serve la password). Se hai perso telefono **e** codici, chiedi allo sviluppatore di togliere la verifica: entrerai con la sola password e potrai riattivarla.

**Telefono nuovo**: togli la verifica (serve la password) e riattivala inquadrando il nuovo QR con il telefono nuovo.

## 5. Cosa fa lo sviluppatore (non si fa dall'area)

Per sicurezza alcune operazioni non esistono nel sito e vanno chieste allo sviluppatore:

- **password dimenticata**: ne imposta una nuova, da cambiare subito dall'area;
- **telefono e codici di riserva persi**: toglie la verifica in due passaggi;
- **account bloccato o compromesso** (accessi che non hai fatto tu): blocca l'account e fa uscire tutti;
- telefono, email, indirizzo, link social, logo, foto, testo della privacy;
- nuove categorie o nuovi formati di prezzo (es. un panino "triple");
- problemi del sito (pagina che non si apre, errori).

## 6. Domande frequenti

| Problema | Cosa fare |
|---|---|
| "Tentativi rimasti: … su 5." o "Ultimo tentativo" | Fermati e ricontrolla la password (maiuscole, tastiera) prima di riprovare. |
| "Hai sbagliato 5 volte…" o "Troppi tentativi: aspetta un minuto e riprova." | Aspetta un minuto e riprova con calma. |
| "Il codice non è corretto o è scaduto." | Scrivi il numero che l'app mostra **adesso** (cambia ogni 30 secondi). Se sbaglia sempre, controlla che data e ora del telefono siano automatiche. |
| "Sessione scaduta" | Normale dopo un'ora di pausa: entra di nuovo. |
| "Modulo scaduto o non valido: ricarica la pagina e riprova." | La pagina è rimasta aperta a lungo: ricaricala e rifai la modifica. |
| Il prezzo non viene accettato | Usa la virgola (7,50), non il punto. |
| "Nella categoria … c'è già una voce chiamata …" | Nella stessa categoria due voci non possono chiamarsi uguali (anche con maiuscole o accenti diversi): cambia il nome o modifica quella che c'è (magari è nascosta). |
| La modifica non si vede nel menù | Controlla che la voce sia "Visibile" e ricarica la pagina del menù. |
| Ho nascosto una voce per sbaglio | Premi **Mostra** accanto alla voce. |
| Ho dimenticato la password | Chiedi allo sviluppatore. |
