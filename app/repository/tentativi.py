from datetime import datetime


class TentativiRepository:
    """
    Accesso alla tabella tentativi_accesso. Non fa commit e non decide il limite: lo fa TentativiService.
    """

    def __init__(self, connessione):
        self._conn = connessione

    def conta_dal(self, ambito: str, impronta_ip: str, dal: datetime) -> int:
        """
        Returns: quanti tentativi sbagliati ha fatto quell'impronta nell'ambito a partire da dal (incluso).
        """
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM tentativi_accesso WHERE ambito = %s AND impronta_ip = %s AND tentato_il >= %s",
                (ambito, impronta_ip, dal),
            )
            return cur.fetchone()[0]

    def inserisci(self, ambito: str, impronta_ip: str, tentato_il: datetime) -> None:
        """
        Registra un tentativo sbagliato.
        """
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tentativi_accesso (ambito, impronta_ip, tentato_il) VALUES (%s, %s, %s)",
                (ambito, impronta_ip, tentato_il),
            )

    def cancella_prima_di(self, prima_di: datetime) -> None:
        """
        Cancella i tentativi più vecchi di prima_di, di tutti gli ambiti: non servono più a contare.
        """
        with self._conn.cursor() as cur:
            cur.execute("DELETE FROM tentativi_accesso WHERE tentato_il < %s", (prima_di,))
