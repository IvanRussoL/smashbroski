CONTENT_SECURITY_POLICY = (
    "default-src 'self'; img-src 'self'; style-src 'self'; script-src 'self'; "
    "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
)

# Il sito non usa fotocamera, microfono, posizione, pagamenti né USB: il browser li nega a tutte le pagine.
PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"


def crea_aggiungi_header(produzione: bool):
    """
    Prepara la funzione after_request che aggiunge gli header di sicurezza a tutte le risposte
    (sezione 7 di PROGETTAZIONE.md, AU-NET07).
    Args: produzione, se True aggiunge anche Strict-Transport-Security (il sito è servito in HTTPS).
    """

    def aggiungi_header(risposta):
        risposta.headers["Content-Security-Policy"] = CONTENT_SECURITY_POLICY
        risposta.headers["X-Content-Type-Options"] = "nosniff"
        risposta.headers["X-Frame-Options"] = "DENY"
        risposta.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        risposta.headers["Permissions-Policy"] = PERMISSIONS_POLICY
        risposta.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        if produzione:
            risposta.headers["Strict-Transport-Security"] = "max-age=31536000"
        return risposta

    return aggiungi_header
