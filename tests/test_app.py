import pytest

from app import create_app


def test_create_app_configurazione_di_test(app):
    assert app.testing is True
    assert app.config["SECRET_KEY"] == "chiave-solo-per-i-test"


def test_create_app_senza_secret_key_errore():
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app({"SECRET_KEY": ""})
