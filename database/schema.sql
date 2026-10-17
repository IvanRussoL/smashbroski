-- Schema del database di SmashBroski Pompei (sezione 4 di docs/PROGETTAZIONE.md).
-- Non crea il database: si esegue dentro quello scelto, così lo stesso file vale per
-- smashbroski (sviluppo) e smashbroski_test (pytest).
-- Le colonne DATETIME sono in UTC; le colonne TIME degli orari sono nell'ora locale del locale.
-- Prezzi in centesimi interi (750 = 7,50 €).

-- Si eliminano prima le tabelle che puntano alle altre, poi quelle a cui puntano.
DROP TABLE IF EXISTS prezzi_voce;
DROP TABLE IF EXISTS voci_menu;
DROP TABLE IF EXISTS formati_prezzo;
DROP TABLE IF EXISTS categorie;
DROP TABLE IF EXISTS orari_settimanali;
DROP TABLE IF EXISTS impostazioni;
DROP TABLE IF EXISTS utenti;

-- Account dell'area riservata: esiste solo il proprietario, quindi nessuna colonna ruolo.
CREATE TABLE utenti (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    attivo        BOOLEAN      NOT NULL DEFAULT TRUE,
    creato_il     DATETIME     NOT NULL DEFAULT (UTC_TIMESTAMP())
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- Le 7 categorie del PDF, fisse: le crea lo script dei dati iniziali.
CREATE TABLE categorie (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    nome      VARCHAR(50)  NOT NULL UNIQUE,
    slug      VARCHAR(50)  NOT NULL UNIQUE,
    posizione TINYINT      NOT NULL,
    nota      VARCHAR(255) NULL,
    -- Solo minuscole, cifre e trattini singoli; 'c' rende il confronto sensibile alle maiuscole.
    CONSTRAINT chk_categorie_slug CHECK (REGEXP_LIKE(slug, '^[a-z0-9]+(-[a-z0-9]+)*$', 'c'))
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- Formati di prezzo di ogni categoria (le colonne di prezzo del PDF).
-- Una categoria senza righe qui ha solo prezzi unici.
CREATE TABLE formati_prezzo (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    categoria_id INT         NOT NULL,
    etichetta    VARCHAR(40) NOT NULL,
    posizione    TINYINT     NOT NULL,
    CONSTRAINT fk_formati_categoria FOREIGN KEY (categoria_id) REFERENCES categorie (id),
    CONSTRAINT uq_formati_etichetta UNIQUE (categoria_id, etichetta)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- Piatti e bevande, gestiti dal proprietario. Una voce non si cancella: si nasconde (attiva = FALSE).
CREATE TABLE voci_menu (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    categoria_id INT          NOT NULL,
    nome         VARCHAR(100) NOT NULL,
    descrizione  VARCHAR(255) NULL,
    edizione     VARCHAR(30)  NULL,
    nota         VARCHAR(255) NULL,
    posizione    SMALLINT     NOT NULL,
    attiva       BOOLEAN      NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_voci_categoria FOREIGN KEY (categoria_id) REFERENCES categorie (id),
    CONSTRAINT uq_voci_nome      UNIQUE (categoria_id, nome),
    INDEX idx_voci_menu_pubblico (categoria_id, attiva, posizione)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- Un prezzo per riga. formato_id vuoto = prezzo unico della voce.
-- "Prezzo unico oppure formati, mai entrambi" e "formato della stessa categoria della voce"
-- non si possono esprimere con un vincolo: le verifica MenuService nella stessa transazione.
CREATE TABLE prezzi_voce (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    voce_id          INT NOT NULL,
    formato_id       INT NULL,
    prezzo_centesimi INT NOT NULL,
    CONSTRAINT fk_prezzi_voce    FOREIGN KEY (voce_id)    REFERENCES voci_menu (id) ON DELETE CASCADE,
    CONSTRAINT fk_prezzi_formato FOREIGN KEY (formato_id) REFERENCES formati_prezzo (id),
    CONSTRAINT uq_prezzi_formato UNIQUE (voce_id, formato_id),
    CONSTRAINT chk_prezzi_positivo CHECK (prezzo_centesimi > 0)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- Calendario settimanale: un turno per riga, nel giorno in cui inizia (1 = lunedì, come isoweekday()).
-- Un giorno senza righe è chiuso. ora_fine < ora_inizio: il turno finisce il giorno dopo.
-- Le sovrapposizioni, anche oltre la mezzanotte, le verifica OrariService.
CREATE TABLE orari_settimanali (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    giorno_settimana TINYINT NOT NULL,
    ora_inizio       TIME    NOT NULL,
    ora_fine         TIME    NOT NULL,
    CONSTRAINT chk_orari_giorno CHECK (giorno_settimana BETWEEN 1 AND 7),
    CONSTRAINT chk_orari_durata CHECK (ora_fine <> ora_inizio),
    INDEX idx_orari_giorno (giorno_settimana)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;

-- Dati del locale mostrati nelle pagine: una sola riga, con id sempre 1.
CREATE TABLE impostazioni (
    id                TINYINT      NOT NULL DEFAULT 1 PRIMARY KEY,
    nome_locale       VARCHAR(100) NOT NULL,
    indirizzo         VARCHAR(255) NOT NULL,
    telefono          VARCHAR(20)  NOT NULL,
    telefono_di_prova BOOLEAN      NOT NULL DEFAULT TRUE,
    email             VARCHAR(255) NOT NULL,
    url_facebook      VARCHAR(255) NOT NULL,
    url_instagram     VARCHAR(255) NOT NULL,
    fuso_orario       VARCHAR(64)  NOT NULL DEFAULT 'Europe/Rome',
    CONSTRAINT chk_impostazioni_riga_unica CHECK (id = 1)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;
