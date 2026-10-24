import pytest

from app import create_app
from app.sicurezza import CONTENT_SECURITY_POLICY, PERMISSIONS_POLICY


@pytest.mark.parametrize("indirizzo", ["/", "/menu", "/info", "/privacy", "/pagina-inesistente"])
def test_header_sicurezza(client, indirizzo):
    header = client.get(indirizzo).headers
    assert header["Content-Security-Policy"] == CONTENT_SECURITY_POLICY
    assert "frame-ancestors 'none'" in header["Content-Security-Policy"]
    assert header["X-Content-Type-Options"] == "nosniff"
    assert header["X-Frame-Options"] == "DENY"
    assert header["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert header["Permissions-Policy"] == PERMISSIONS_POLICY
    assert header["Cross-Origin-Opener-Policy"] == "same-origin"


def test_hsts_solo_produzione(app, database_di_prova):
    assert "Strict-Transport-Security" not in app.test_client().get("/privacy").headers
    configurazione = {"TESTING": True, "SECRET_KEY": "chiave-solo-per-i-test",
                      "DB_NAME": app.config["DB_NAME"], "PRODUZIONE": True}
    produzione = create_app(configurazione).test_client()
    assert produzione.get("/privacy").headers["Strict-Transport-Security"] == "max-age=31536000"
