import click
from flask import current_app
from flask.cli import with_appcontext

from app.db import ottieni_connessione
from app.eccezioni import DatiNonValidiError
from app.repository.utente import UtenteRepository
from app.servizi.auth import LUNGHEZZA_MINIMA_PASSWORD, AuthService
from app.servizi.due_passaggi import DuePassaggiService


@click.command("crea-proprietario")
@with_appcontext
def crea_proprietario():
    """
    Crea l'account del proprietario da terminale: flask --app app crea-proprietario.
    La password si scrive senza che compaia sullo schermo e va ripetuta.
    """
    email = click.prompt("Email")
    password = click.prompt(
        f"Password (almeno {LUNGHEZZA_MINIMA_PASSWORD} caratteri)",
        hide_input=True,
        confirmation_prompt="Ripeti la password",
    )
    try:
        utente_id = AuthService(ottieni_connessione()).crea_proprietario(email, password)
    except DatiNonValidiError as errore:
        raise click.ClickException(" ".join(errore.messaggi))
    click.echo(f"Proprietario creato (id {utente_id}).")


@click.command("reimposta-password")
@with_appcontext
def reimposta_password():
    """
    Nuova password per un account, quando il proprietario l'ha dimenticata:
    flask --app app reimposta-password. Solo per lo sviluppatore, mai dal sito.
    """
    email = click.prompt("Email dell'account")
    password = click.prompt(
        f"Nuova password (almeno {LUNGHEZZA_MINIMA_PASSWORD} caratteri)",
        hide_input=True,
        confirmation_prompt="Ripeti la password",
    )
    try:
        AuthService(ottieni_connessione()).reimposta_password(email, password)
    except DatiNonValidiError as errore:
        raise click.ClickException(" ".join(errore.messaggi))
    click.echo("Password reimpostata. Comunicala al proprietario e chiedigli di cambiarla dall'area.")


@click.command("disattiva-proprietario")
@click.argument("email")
@with_appcontext
def disattiva_proprietario(email):
    """
    Blocca un account: non entra più e chi è già dentro esce alla richiesta successiva.
    Esempio: flask --app app disattiva-proprietario proprietario@example.com
    """
    _imposta_attivo(email, False)
    click.echo("Account disattivato.")


@click.command("riattiva-proprietario")
@click.argument("email")
@with_appcontext
def riattiva_proprietario(email):
    """
    Sblocca un account disattivato. Esempio: flask --app app riattiva-proprietario proprietario@example.com
    """
    _imposta_attivo(email, True)
    click.echo("Account riattivato.")


def _imposta_attivo(email: str, attivo: bool) -> None:
    try:
        AuthService(ottieni_connessione()).imposta_attivo(email, attivo)
    except DatiNonValidiError as errore:
        raise click.ClickException(" ".join(errore.messaggi))


@click.command("disattiva-due-passaggi")
@click.argument("email")
@with_appcontext
def disattiva_due_passaggi(email):
    """
    Toglie la verifica in due passaggi quando il proprietario ha perso il telefono e i codici di
    riserva: entrerà con la sola password e potrà riattivarla dall'area.
    Esempio: flask --app app disattiva-due-passaggi proprietario@example.com
    """
    connessione = ottieni_connessione()
    utente = UtenteRepository(connessione).leggi_per_email((email or "").strip())
    if utente is None:
        raise click.ClickException("Nessun account con questa email.")
    DuePassaggiService(connessione, current_app.secret_key).disattiva(utente.id)
    click.echo("Verifica in due passaggi tolta: il proprietario entra con la sola password.")

