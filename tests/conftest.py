import pytest

from app import create_app

CONFIGURAZIONE_TEST = {"TESTING": True, "SECRET_KEY": "chiave-solo-per-i-test"}


@pytest.fixture
def app():
    """
    App creata con la configurazione di test, indipendente dal file .env.
    """
    return create_app(CONFIGURAZIONE_TEST)
