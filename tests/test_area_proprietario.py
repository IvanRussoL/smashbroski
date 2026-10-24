from app.servizi.auth import AuthService

BURGER, SALAD = 3, 2
SINGLE_SALAD, PANINO_SINGLE, MENU_SINGLE = 3, 5, 7


def html(risposta) -> str:
    return risposta.get_data(as_text=True)


def dati_voce(**campi) -> dict:
    dati = {"nome": "", "descrizione": "", "edizione": "", "nota": "", "posizione": "", "prezzo_unico": ""}
    dati.update(campi)
    return dati


# --- Voci ---

def test_indice_mostra_tutte_le_voci(client_proprietario):
    pagina = html(client_proprietario.get("/proprietario/"))
    assert pagina.count("Modifica</a>") == 25
    assert "Aggiungi una voce in Kids Menù" in pagina


def test_barra_area_distinta_dalla_navbar_e_pagina_corrente(client_proprietario):
    indice = html(client_proprietario.get("/proprietario/"))
    assert 'aria-current="page">Gestisci il menù</a>' in indice
    assert 'aria-current="page">Gestisci gli orari</a>' not in indice
    orari = html(client_proprietario.get("/proprietario/orari"))
    assert 'aria-current="page">Gestisci gli orari</a>' in orari


def test_indice_categorie_nella_gestione_del_menu(client_proprietario):
    pagina = html(client_proprietario.get("/proprietario/"))
    assert 'aria-label="Categorie da gestire"' in pagina
    assert pagina.count('<li><a href="#') == 7
    assert 'href="#the-originals"' in pagina and 'id="the-originals"' in pagina


def test_nuova_voce_compare_nel_menu(client_proprietario, database_modificato):
    risposta = client_proprietario.post(f"/proprietario/voci/nuova?categoria={BURGER}", data=dati_voce(
        nome="Smash Pompei", descrizione="Hamburger, provola", **{f"prezzo_{PANINO_SINGLE}": "8,50"},
    ))
    assert risposta.status_code == 302
    menu = html(client_proprietario.get("/menu"))
    assert "Smash Pompei" in menu
    assert "8,50 €" in menu.split("Smash Pompei")[1].split("</article>")[0]


def test_dati_non_validi_400(client_proprietario):
    risposta = client_proprietario.post(f"/proprietario/voci/nuova?categoria={BURGER}", data=dati_voce(
        nome="Prezzo sbagliato", **{f"prezzo_{PANINO_SINGLE}": "abc"},
    ))
    assert risposta.status_code == 400
    pagina = html(risposta)
    assert "non valido" in pagina
    assert 'value="Prezzo sbagliato"' in pagina  # il modulo tiene i dati scritti


def test_formato_di_altra_categoria_manomesso(client_proprietario):
    risposta = client_proprietario.post(f"/proprietario/voci/nuova?categoria={BURGER}", data=dati_voce(
        nome="Manomesso", **{f"prezzo_{SINGLE_SALAD}": "8"},
    ))
    assert risposta.status_code == 400
    assert "Formato di prezzo non valido" in html(risposta)


def test_modulo_modifica_precompilato(client_proprietario):
    pagina = html(client_proprietario.get("/proprietario/voci/6"))  # Smash Burger
    assert 'value="Smash Burger"' in pagina
    assert f'name="prezzo_{PANINO_SINGLE}" inputmode="decimal" value="7,00"' in pagina


def test_modifica_voce(client_proprietario, database_modificato):
    risposta = client_proprietario.post("/proprietario/voci/6", data=dati_voce(
        nome="Smash Burger", descrizione="Hamburger, insalata, pomodoro, salsa smash", posizione="1",
        **{f"prezzo_{PANINO_SINGLE}": "7,20", f"prezzo_{MENU_SINGLE}": "10"},
    ))
    assert risposta.status_code == 302
    voce = html(client_proprietario.get("/menu")).split("Smash Burger</span>")[1].split("</article>")[0]
    assert "7,20 €" in voce
    assert "double" not in voce


def test_nascondi_e_mostra_voce(client_proprietario, database_modificato):
    client_proprietario.post("/proprietario/voci/6/visibilita", data={"attiva": "0"})
    assert "Smash Burger</span>" not in html(client_proprietario.get("/menu"))
    client_proprietario.post("/proprietario/voci/6/visibilita", data={"attiva": "1"})
    assert "Smash Burger</span>" in html(client_proprietario.get("/menu"))


def test_voce_inesistente_404(client_proprietario):
    assert client_proprietario.get("/proprietario/voci/99999").status_code == 404
    assert client_proprietario.post("/proprietario/voci/99999/visibilita", data={"attiva": "0"}).status_code == 404
    assert client_proprietario.get("/proprietario/voci/nuova?categoria=99").status_code == 404


# --- Orari ---

def test_orari_precompilati(client_proprietario):
    pagina = html(client_proprietario.get("/proprietario/orari"))
    assert 'type="time" value="18:00"' in pagina
    assert 'type="time" value="01:00"' in pagina


def test_salva_orari(client_proprietario, database_modificato):
    risposta = client_proprietario.post("/proprietario/orari", data={
        "giorno": ["1", "1", "2", "3"],
        "inizio": ["19:00", "", "", "12:00"],
        "fine": ["23:00", "", "", "15:00"],
    })
    assert risposta.status_code == 302
    info = html(client_proprietario.get("/info"))  # gli orari sono nella pagina Orari e contatti
    assert "19:00–23:00" in info
    assert "18:00–01:00" not in info


def test_orari_sovrapposti_rifiutati(client_proprietario):
    risposta = client_proprietario.post("/proprietario/orari", data={
        "giorno": ["7", "1"], "inizio": ["18:00", "01:00"], "fine": ["02:00", "03:00"],
    })
    assert risposta.status_code == 400
    pagina = html(risposta)
    assert "Turni sovrapposti: domenica 18:00-02:00 e lunedì 01:00-03:00." in pagina
    assert 'type="time" value="03:00"' in pagina  # il modulo tiene i dati scritti
    assert "18:00–01:00" in html(client_proprietario.get("/info"))  # orari invariati


# --- Comando da terminale ---

def test_comando_crea_proprietario(app, database_modificato):
    risultato = app.test_cli_runner().invoke(
        args=["crea-proprietario"], input="nuovo@example.com\nuna-password-sicura\nuna-password-sicura\n",
    )
    assert risultato.exit_code == 0, risultato.output
    assert "Proprietario creato" in risultato.output
    assert AuthService(database_modificato).login("nuovo@example.com", "una-password-sicura") is not None


def test_comando_crea_proprietario_password_corta(app, database_di_prova):
    risultato = app.test_cli_runner().invoke(args=["crea-proprietario"], input="corta@example.com\ncorta\ncorta\n")
    assert risultato.exit_code != 0
    assert "La password deve avere almeno 12 caratteri." in risultato.output


# --- Cambio di categoria ---

THE_ORIGINALS, BURGER_ORIGINALS, MENU_ORIGINALS = 7, 9, 10


def test_cambio_categoria_mostra_i_nuovi_formati(client_proprietario):
    pagina = html(client_proprietario.get(f"/proprietario/voci/6?categoria={THE_ORIGINALS}"))
    assert "Stai spostando la voce in <strong>The Originals</strong>" in pagina
    assert f'name="prezzo_{BURGER_ORIGINALS}"' in pagina
    assert f'name="prezzo_{PANINO_SINGLE}"' not in pagina
    assert f'name="categoria_id" value="{THE_ORIGINALS}"' in pagina
    assert 'value="Smash Burger"' in pagina  # gli altri campi restano compilati


def test_cambio_categoria_salvato(client_proprietario, database_modificato):
    risposta = client_proprietario.post("/proprietario/voci/6", data=dati_voce(
        categoria_id=str(THE_ORIGINALS), nome="Smash Burger",
        **{f"prezzo_{BURGER_ORIGINALS}": "8", f"prezzo_{MENU_ORIGINALS}": "12"},
    ))
    assert risposta.status_code == 302
    assert risposta.headers["Location"].endswith("#the-originals")
    menu = html(client_proprietario.get("/menu"))
    originals = menu.split('id="the-originals"')[1]
    assert "Smash Burger</span>" in originals


def test_cambio_categoria_senza_salvare_non_sposta(client_proprietario):
    client_proprietario.get(f"/proprietario/voci/6?categoria={THE_ORIGINALS}")
    burger = html(client_proprietario.get("/menu")).split('id="burger"')[1].split('id="kids-menu"')[0]
    assert "Smash Burger</span>" in burger
