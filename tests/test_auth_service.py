import pytest
from argon2 import PasswordHasher

from app.eccezioni import DatiNonValidiError, NonTrovatoError
from app.modelli.utente import Utente
from app.repository.utente import UtenteRepository
from app.servizi.auth import AuthService

EMAIL = "proprietario.auth@example.com"
PASSWORD = "una-password-lunga"


class HasherSpia(PasswordHasher):
    """
    PasswordHasher che ricorda gli hash su cui è stata eseguita la verifica.
    """

    def __init__(self):
        super().__init__()
        self.verificati = []

    def verify(self, password_hash, password):
        self.verificati.append(password_hash)
        return super().verify(password_hash, password)


@pytest.fixture
def proprietario(connessione):
    """
    Id di un proprietario di prova; a fine test viene annullato con il resto.
    """
    return AuthService(connessione).crea_proprietario(EMAIL, PASSWORD)


def test_login_corretto(connessione, proprietario):
    utente = AuthService(connessione).login(EMAIL, PASSWORD)
    assert utente is not None
    assert utente.id == proprietario


def test_login_email_senza_distinguere_maiuscole(connessione, proprietario):
    assert AuthService(connessione).login("  Proprietario.Auth@Example.com ", PASSWORD).id == proprietario


def test_login_password_errata(connessione, proprietario):
    assert AuthService(connessione).login(EMAIL, "password-sbagliata") is None


def test_login_email_inesistente_verifica_comunque(connessione):
    spia = HasherSpia()
    servizio = AuthService(connessione, hasher=spia)
    assert servizio.login("nessuno@example.com", PASSWORD) is None
    assert len(spia.verificati) == 1  # la verifica Argon2 è stata eseguita lo stesso
    assert spia.verificati[0].startswith("$argon2id$")


def test_login_account_disattivato(connessione):
    hasher = PasswordHasher()
    UtenteRepository(connessione).inserisci(
        Utente("disattivato@example.com", hasher.hash(PASSWORD), attivo=False)
    )
    assert AuthService(connessione).login("disattivato@example.com", PASSWORD) is None


def test_hash_argon2id(connessione, proprietario):
    password_hash = UtenteRepository(connessione).leggi_per_id(proprietario).password_hash
    assert password_hash.startswith("$argon2id$")
    assert PASSWORD not in password_hash


def test_rehash_parametri_superati(connessione):
    debole = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)
    repo = UtenteRepository(connessione)
    utente_id = repo.inserisci(Utente("rehash@example.com", debole.hash(PASSWORD)))
    vecchio = repo.leggi_per_id(utente_id).password_hash

    assert AuthService(connessione).login("rehash@example.com", PASSWORD) is not None
    nuovo = repo.leggi_per_id(utente_id).password_hash
    assert nuovo != vecchio
    assert PasswordHasher().check_needs_rehash(nuovo) is False
    assert AuthService(connessione).login("rehash@example.com", PASSWORD) is not None


def test_crea_proprietario_password_corta(connessione):
    with pytest.raises(DatiNonValidiError):
        AuthService(connessione).crea_proprietario("corta@example.com", "x" * 11)


def test_crea_proprietario_password_di_12_caratteri(connessione):
    assert AuthService(connessione).crea_proprietario("dodici@example.com", "x" * 12) > 0


def test_crea_proprietario_email_duplicata(connessione, proprietario):
    with pytest.raises(DatiNonValidiError):
        AuthService(connessione).crea_proprietario(EMAIL.upper(), PASSWORD)


@pytest.mark.parametrize("email", ["", "senza-chiocciola", "x" * 250 + "@example.com"])
def test_crea_proprietario_email_non_valida(connessione, email):
    with pytest.raises(DatiNonValidiError):
        AuthService(connessione).crea_proprietario(email, PASSWORD)


def test_crea_proprietario_email_salvata_minuscola(connessione):
    utente_id = AuthService(connessione).crea_proprietario("Nuovo.Proprietario@Example.com", PASSWORD)
    assert UtenteRepository(connessione).leggi_per_id(utente_id).email == "nuovo.proprietario@example.com"


# --- Cambio e reimpostazione della password, account attivo ---

NUOVA = "una-nuova-password-lunga"


def test_cambia_password(connessione, proprietario):
    servizio = AuthService(connessione)
    servizio.cambia_password(proprietario, PASSWORD, NUOVA, NUOVA)
    assert servizio.login(EMAIL, NUOVA).id == proprietario
    assert servizio.login(EMAIL, PASSWORD) is None


def test_cambia_password_attuale_sbagliata(connessione, proprietario):
    with pytest.raises(DatiNonValidiError) as errore:
        AuthService(connessione).cambia_password(proprietario, "sbagliata", NUOVA, NUOVA)
    assert errore.value.messaggi == ["La password attuale non è corretta."]
    assert AuthService(connessione).login(EMAIL, PASSWORD) is not None  # invariata


def test_cambia_password_errori_raccolti(connessione, proprietario):
    with pytest.raises(DatiNonValidiError) as errore:
        AuthService(connessione).cambia_password(proprietario, "sbagliata", "corta", "diversa")
    assert errore.value.messaggi == [
        "La password attuale non è corretta.",
        "La nuova password deve avere almeno 12 caratteri.",
        "La nuova password e la conferma non coincidono.",
    ]


def test_cambia_password_uguale_alla_attuale(connessione, proprietario):
    with pytest.raises(DatiNonValidiError) as errore:
        AuthService(connessione).cambia_password(proprietario, PASSWORD, PASSWORD, PASSWORD)
    assert errore.value.messaggi == ["La nuova password deve essere diversa da quella attuale."]


def test_cambia_password_utente_inesistente(connessione):
    with pytest.raises(NonTrovatoError):
        AuthService(connessione).cambia_password(9999, PASSWORD, NUOVA, NUOVA)


def test_reimposta_password(connessione, proprietario):
    servizio = AuthService(connessione)
    servizio.reimposta_password(" Proprietario.Auth@Example.com ", NUOVA)
    assert servizio.login(EMAIL, NUOVA).id == proprietario


def test_reimposta_password_email_sconosciuta_o_corta(connessione, proprietario):
    with pytest.raises(DatiNonValidiError, match="Nessun account"):
        AuthService(connessione).reimposta_password("nessuno@example.com", NUOVA)
    with pytest.raises(DatiNonValidiError, match="almeno 12"):
        AuthService(connessione).reimposta_password(EMAIL, "corta")


def test_disattiva_e_riattiva(connessione, proprietario):
    servizio = AuthService(connessione)
    servizio.imposta_attivo(EMAIL, False)
    assert servizio.login(EMAIL, PASSWORD) is None
    servizio.imposta_attivo(EMAIL, True)
    assert servizio.login(EMAIL, PASSWORD).id == proprietario



def test_password_troppo_lunga_rifiutata(connessione, proprietario):
    lunga = "x" * 129
    servizio = AuthService(connessione)
    assert servizio.login(EMAIL, PASSWORD + lunga) is None
    with pytest.raises(DatiNonValidiError, match="al massimo 128 caratteri"):
        servizio.crea_proprietario("altro@example.com", lunga)
    with pytest.raises(DatiNonValidiError, match="al massimo 128 caratteri"):
        servizio.cambia_password(proprietario, PASSWORD, lunga, lunga)
    with pytest.raises(DatiNonValidiError, match="al massimo 128 caratteri"):
        servizio.reimposta_password(EMAIL, lunga)


def test_password_di_128_caratteri_accettata(connessione, proprietario):
    massima = "y" * 128
    servizio = AuthService(connessione)
    servizio.cambia_password(proprietario, PASSWORD, massima, massima)
    assert servizio.login(EMAIL, massima) is not None
