import pytest
from argon2 import PasswordHasher

from app.eccezioni import DatiNonValidiError
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
