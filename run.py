from dotenv import load_dotenv

from app import create_app

load_dotenv()
app = create_app()

if __name__ == "__main__":
    # Solo per lo sviluppo sul computer: il debugger permette di eseguire codice dal browser.
    # Online il sito si avvia con un server WSGI (docs/GESTIONE_SITO.md, sezione 8).
    if app.config["PRODUZIONE"]:
        raise SystemExit("PRODUZIONE=1: avviare il sito con un server WSGI, non con run.py.")
    app.run(debug=True)
