import click
from flask.cli import with_appcontext

from app.db import ottieni_connessione
from app.eccezioni import DatiNonValidiError
from app.servizi.auth import LUNGHEZZA_MINIMA_PASSWORD, AuthService


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
