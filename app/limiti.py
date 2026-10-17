from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Limite ai tentativi di login sbagliati, per indirizzo IP. I conteggi stanno nella memoria del
# processo: basta con un solo server; con più processi servirebbe un archivio comune (es. Redis).
# L'indirizzo IP serve solo a contare e non viene salvato.
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")

LIMITE_TENTATIVI_LOGIN = "5 per minute"


def tentativo_fallito(risposta) -> bool:
    """
    Conta solo i login sbagliati (risposta 400): chi entra al primo colpo non consuma il limite.
    """
    return risposta.status_code == 400
