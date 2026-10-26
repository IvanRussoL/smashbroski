# SmashBroski Pompei – sito di un'hamburgeria

> **Progetto dimostrativo di portfolio e di studio.** SmashBroski è un locale fittizio: nome, logo e indirizzo sono inventati; telefono, email e social sono segnaposto. Il progetto nasce da un audit QA del sito di un locale reale, qui anonimizzato.

Sito in Flask per un'hamburgeria: home responsive con orari e stato "aperto ora", menù digitale in HTML al posto del PDF, area proprietario protetta per aggiornare menù e orari.

Il progetto nasce da un audit QA del sito di partenza (32 casi di test, 21 FAIL). Ogni requisito del nuovo sito è collegato al FAIL che risolve.

**Stato:** Fase 2 completata: sito pubblico, area proprietario (Argon2id, CSRF, limite dei tentativi, verifica in due passaggi facoltativa) e 268 test pytest superati.

**Tecnologie:** Python 3.13, Flask 3, MySQL 8, Jinja2, argon2-cffi, Flask-WTF, pyotp, pytest.

## Documentazione

- [Progettazione](docs/PROGETTAZIONE.md): obiettivo, requisiti, regole, modello dati, architettura, sicurezza
- [Wireframe](docs/WIREFRAME.md): Home e Menù, mobile e desktop
- [Piano di test](docs/PIANO_TEST.md): casi manuali, test pytest, matrice audit → requisiti → test
- [Gestione del sito](docs/GESTIONE_SITO.md): ambiente, avvio, test, comandi dello sviluppatore, pubblicazione
- [Manuale del proprietario](docs/MANUALE_PROPRIETARIO.md): come si aggiornano menù e orari
- [DEVLOG](DEVLOG.md): decisioni prese, con motivazioni e alternative scartate
