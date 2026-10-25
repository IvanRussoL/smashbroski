-- Aggiornamento di un database già esistente (sviluppo o online) senza ricaricare tutto lo schema:
-- colonne della verifica in due passaggi in utenti e tabella dei codici di riserva.
-- Si esegue una volta, come root in MySQL Workbench, sul database dell'app (dopo quello del 24/10).
ALTER TABLE utenti
    ADD COLUMN totp_segreto      VARCHAR(255) NULL,
    ADD COLUMN totp_attivo       BOOLEAN      NOT NULL DEFAULT FALSE,
    ADD COLUMN totp_ultimo_passo BIGINT       NULL;

CREATE TABLE IF NOT EXISTS codici_riserva (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    utente_id   INT          NOT NULL,
    codice_hash VARCHAR(255) NOT NULL,
    usato_il    DATETIME     NULL,
    CONSTRAINT fk_codici_utente FOREIGN KEY (utente_id) REFERENCES utenti (id) ON DELETE CASCADE,
    INDEX idx_codici_utente (utente_id, usato_il)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
