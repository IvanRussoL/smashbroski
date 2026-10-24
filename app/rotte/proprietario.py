import re
from collections import defaultdict

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from app.db import ottieni_connessione
from app.eccezioni import DatiNonValidiError
from app.formato import prezzo_per_modulo
from app.limiti import LIMITE_TENTATIVI_LOGIN, limiter, tentativo_fallito
from app.repository.utente import UtenteRepository
from app.servizi.auth import AuthService
from app.servizi.menu import DatiVoce, MenuService
from app.servizi.orari import NOMI_GIORNI, OrariService

bp = Blueprint("proprietario", __name__, url_prefix="/proprietario")

_CAMPO_PREZZO_FORMATO = re.compile(r"^prezzo_(\d+)$")
RIGHE_LIBERE_PER_GIORNO = 1
RIGHE_MINIME_PER_GIORNO = 2


@bp.before_request
def richiedi_proprietario():
    """
    Eseguito prima di ogni rotta di questo Blueprint, comprese quelle aggiunte in futuro (nega per
    default). L'utente si ricarica dal database a ogni richiesta: un account disattivato perde
    subito l'accesso.
    """
    utente_id = session.get("utente_id")
    utente = UtenteRepository(ottieni_connessione()).leggi_per_id(utente_id) if utente_id else None
    if utente is None or not utente.attivo:
        session.clear()
        return redirect(url_for("auth.login"))
    g.utente = utente


@bp.after_request
def non_salvare_in_cache(risposta):
    """
    Le pagine riservate non restano nella cache del browser (es. dopo il logout con il tasto Indietro).
    """
    risposta.headers["Cache-Control"] = "no-store"
    return risposta


# --- Menù ---

@bp.get("/")
def indice():
    return render_template("proprietario/indice.html", categorie=MenuService(ottieni_connessione()).menu_completo())


def _dati_voce_dal_modulo(categoria_id: int) -> DatiVoce:
    """
    Legge il modulo della voce. I prezzi per formato arrivano nei campi prezzo_<id del formato>:
    si leggono tutti quelli inviati, così un formato di un'altra categoria o ripetuto viene
    rifiutato dal servizio invece di essere ignorato.
    """
    modulo = request.form
    prezzi_formati = [
        (_CAMPO_PREZZO_FORMATO.match(nome).group(1), valore)
        for nome, valore in modulo.items(multi=True)
        if _CAMPO_PREZZO_FORMATO.match(nome)
    ]
    return DatiVoce(
        categoria_id=categoria_id,
        nome=modulo.get("nome", ""),
        descrizione=modulo.get("descrizione", ""),
        edizione=modulo.get("edizione", ""),
        nota=modulo.get("nota", ""),
        posizione=modulo.get("posizione", ""),
        prezzo_unico=modulo.get("prezzo_unico", ""),
        prezzi_formati=prezzi_formati,
    )


def _valori_da_voce(voce) -> dict:
    """
    Valori iniziali del modulo di modifica, con i prezzi scritti come li scrive il proprietario.
    """
    valori = {"nome": voce.nome, "descrizione": voce.descrizione or "", "edizione": voce.edizione or "",
              "nota": voce.nota or "", "posizione": str(voce.posizione), "prezzo_unico": ""}
    for prezzo in voce.prezzi:
        chiave = "prezzo_unico" if prezzo.formato_id is None else f"prezzo_{prezzo.formato_id}"
        valori[chiave] = prezzo_per_modulo(prezzo.prezzo_centesimi)
    return valori


@bp.route("/voci/nuova", methods=["GET", "POST"])
def nuova_voce():
    """
    Nuova voce in una categoria, indicata nell'indirizzo (?categoria=3): il modulo mostra i
    formati di prezzo di quella categoria.
    """
    servizio = MenuService(ottieni_connessione())
    categoria = servizio.leggi_categoria(request.args.get("categoria", ""))
    if request.method == "POST":
        try:
            servizio.crea_voce(_dati_voce_dal_modulo(categoria.id))
        except DatiNonValidiError as errore:
            return render_template("proprietario/voce.html", categoria=categoria, voce=None,
                                   valori=request.form, errori=errore.messaggi), 400
        flash("Voce aggiunta.")
        return redirect(url_for("proprietario.indice") + f"#{categoria.slug}")
    return render_template("proprietario/voce.html", categoria=categoria, voce=None, valori={})


@bp.route("/voci/<int:voce_id>", methods=["GET", "POST"])
def modifica_voce(voce_id: int):
    """
    Modifica di una voce. Per spostarla in un'altra categoria il proprietario la sceglie dall'elenco:
    la pagina si ricarica con ?categoria=<id> e mostra i formati di prezzo della nuova categoria,
    da compilare di nuovo (i formati della categoria di partenza non valgono nell'altra).
    """
    servizio = MenuService(ottieni_connessione())
    voce = servizio.leggi_voce(voce_id)
    if request.method == "POST":
        categoria = servizio.leggi_categoria(request.form.get("categoria_id", voce.categoria_id))
    else:
        categoria = servizio.leggi_categoria(request.args.get("categoria", voce.categoria_id))
    spostamento = categoria.id != voce.categoria_id

    if request.method == "POST":
        try:
            servizio.modifica_voce(voce_id, _dati_voce_dal_modulo(categoria.id))
        except DatiNonValidiError as errore:
            return render_template("proprietario/voce.html", categoria=categoria, voce=voce,
                                   valori=request.form, errori=errore.messaggi, spostamento=spostamento,
                                   categorie=servizio.categorie()), 400
        flash(f"Voce spostata in {categoria.nome} e salvata." if spostamento else "Voce salvata.")
        return redirect(url_for("proprietario.indice") + f"#{categoria.slug}")

    valori = _valori_da_voce(voce)
    if spostamento:
        # I prezzi per formato della vecchia categoria non valgono nella nuova; la voce va in fondo.
        valori = {chiave: valore for chiave, valore in valori.items() if not chiave.startswith("prezzo_")
                  or chiave == "prezzo_unico"}
        valori["posizione"] = ""
    return render_template("proprietario/voce.html", categoria=categoria, voce=voce, valori=valori,
                           spostamento=spostamento, categorie=servizio.categorie())


@bp.post("/voci/<int:voce_id>/visibilita")
def visibilita_voce(voce_id: int):
    """
    Nasconde o rimostra una voce: il modulo invia attiva = 1 (mostra) oppure 0 (nascondi).
    """
    servizio = MenuService(ottieni_connessione())
    attiva = request.form.get("attiva") == "1"
    servizio.imposta_visibilita(voce_id, attiva)
    voce = servizio.leggi_voce(voce_id)
    flash(f"«{voce.nome}» {'di nuovo visibile' if attiva else 'nascosta'} nel menù.")
    categoria = servizio.leggi_categoria(voce.categoria_id)
    return redirect(url_for("proprietario.indice") + f"#{categoria.slug}")


# --- Orari ---

def _righe_orari(turni_per_giorno: dict) -> list[dict]:
    """
    Righe del modulo degli orari: per ogni giorno i turni esistenti più una riga libera,
    con almeno due righe per giorno.
    """
    giorni = []
    for numero, nome in NOMI_GIORNI.items():
        turni = turni_per_giorno.get(numero, [])
        righe = turni + [("", "")] * max(RIGHE_LIBERE_PER_GIORNO, RIGHE_MINIME_PER_GIORNO - len(turni))
        giorni.append({"numero": numero, "nome": nome.capitalize(), "righe": righe})
    return giorni


@bp.route("/orari", methods=["GET", "POST"])
def orari():
    servizio = OrariService(ottieni_connessione())
    if request.method == "POST":
        righe = list(zip(request.form.getlist("giorno"), request.form.getlist("inizio"),
                         request.form.getlist("fine")))
        try:
            servizio.salva_turni(righe)
        except DatiNonValidiError as errore:
            inviati = defaultdict(list)
            for giorno, inizio, fine in righe:
                if giorno.isdigit() and (inizio or fine):
                    inviati[int(giorno)].append((inizio, fine))
            return render_template("proprietario/orari.html", giorni=_righe_orari(inviati),
                                   errori=errore.messaggi), 400
        flash("Orari salvati.")
        return redirect(url_for("proprietario.orari"))

    esistenti = defaultdict(list)
    for turno in servizio.leggi_turni():
        esistenti[turno.giorno_settimana].append(
            (turno.ora_inizio.strftime("%H:%M"), turno.ora_fine.strftime("%H:%M"))
        )
    return render_template("proprietario/orari.html", giorni=_righe_orari(esistenti))


# --- Password ---

@bp.route("/password", methods=["GET", "POST"])
@limiter.limit(LIMITE_TENTATIVI_LOGIN, methods=["POST"], deduct_when=tentativo_fallito)
def password():
    """
    Cambio della password del proprietario. Stesso limite del login sui tentativi sbagliati, così
    con la sessione aperta non si può provare la password attuale all'infinito. Dopo il cambio
    la sessione viene rinnovata.
    """
    if request.method == "POST":
        try:
            AuthService(ottieni_connessione()).cambia_password(
                g.utente.id, request.form.get("attuale", ""), request.form.get("nuova", ""),
                request.form.get("conferma", ""),
            )
        except DatiNonValidiError as errore:
            return render_template("proprietario/password.html", errori=errore.messaggi), 400
        session.clear()
        session["utente_id"] = g.utente.id
        session.permanent = True
        flash("Password cambiata. Da ora entra con quella nuova.")
        return redirect(url_for("proprietario.password"))
    return render_template("proprietario/password.html")

