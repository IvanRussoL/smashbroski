-- Aggiornamento di un database già esistente (sviluppo o online) senza ricaricare tutto lo schema:
-- aggiunge la tabella dei tentativi di accesso (schema.sql la crea già nei database nuovi).
-- Si esegue una volta, come root in MySQL Workbench, sul database dell'app.
CREATE TABLE IF NOT EXISTS tentativi_accesso (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    ambito      VARCHAR(20) NOT NULL,
    impronta_ip CHAR(64)    NOT NULL,
    tentato_il  DATETIME(6) NOT NULL,
    INDEX idx_tentativi_conteggio (ambito, impronta_ip, tentato_il),
    INDEX idx_tentativi_pulizia (tentato_il)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
