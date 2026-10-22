-- Dati iniziali di SmashBroski Pompei (sezione 4 di docs/PROGETTAZIONE.md).
-- Si esegue subito dopo schema.sql, nello stesso database: le tabelle devono essere vuote.
-- Prezzi letti a vista dal rendering di Menu_digitale.pdf ("Menù a parete 85,8x140,5cm 2025"),
-- non dal suo livello di testo, e scritti in centesimi (750 = 7,50 €).
-- Gli id sono scritti a mano perché le righe successive li usano; le tabelle sono appena create,
-- quindi partono da 1.

START TRANSACTION;

-- Dati del locale. FITTIZI (segnaposto): telefono, WhatsApp, email, Facebook e Instagram.
-- telefono_di_prova = TRUE: il sito mostra "numero di prova" e lo esclude dal JSON-LD.
-- WhatsApp di prova: +39 300 000 0000, prefisso cellulare non assegnato, quindi non è il numero di nessuno.
INSERT INTO impostazioni
    (id, nome_locale, indirizzo, telefono, telefono_di_prova, whatsapp, whatsapp_di_prova, email, url_facebook, url_instagram, fuso_orario)
VALUES
    (1, 'SmashBroski Pompei', 'Vico dei Paninari, 7 - 80045 Pompei (NA)', '+390810000000', TRUE,
     '+393000000000', TRUE,
     'info@example.com', 'https://example.com/facebook-segnaposto', 'https://example.com/instagram-segnaposto',
     'Europe/Rome');

-- Orari settimanali: 1 = lunedì ... 7 = domenica. Martedì (2) chiuso: nessuna riga.
-- Un turno appartiene al giorno in cui inizia: 18:00-01:00 finisce il giorno dopo.
INSERT INTO orari_settimanali (giorno_settimana, ora_inizio, ora_fine) VALUES
    (1, '12:00', '15:00'), (1, '18:00', '01:00'),
    (3, '12:00', '15:00'), (3, '18:00', '01:00'),
    (4, '12:00', '15:00'), (4, '18:00', '01:00'),
    (5, '12:00', '15:00'), (5, '18:00', '01:00'),
    (6, '18:00', '02:00'),
    (7, '18:00', '02:00');

-- Le 7 categorie, nell'ordine del PDF.
INSERT INTO categorie (id, nome, slug, posizione, nota) VALUES
    (1, 'Starters',      'starters',      1, NULL),
    (2, 'Salad',         'salad',         2, NULL),
    (3, 'Burger',        'burger',        3, 'Brooo, prova il menù: 1 panino, 1 porzione di patatine stick, 1 bibita a scelta (Coca-Cola, Fanta, Sprite o Acqua).'),
    (4, 'Kids Menù',     'kids-menu',     4, NULL),
    (5, 'Soft Drinks',   'soft-drinks',   5, NULL),
    (6, 'Beers',         'beers',         6, NULL),
    (7, 'The Originals', 'the-originals', 7, 'Ortaggio su base stagionale');

-- Formati di prezzo (le colonne del PDF). Kids Menù, Soft Drinks e Beers non ne hanno.
INSERT INTO formati_prezzo (id, categoria_id, etichetta, posizione) VALUES
    (1,  1, '5 pz',                1),
    (2,  1, '10 pz',               2),
    (3,  2, 'Single',              1),
    (4,  2, 'Menù',                2),
    (5,  3, 'Panino single hamb.', 1),
    (6,  3, 'Panino double hamb.', 2),
    (7,  3, 'Menù single hamb.',   3),
    (8,  3, 'Menù double hamb.',   4),
    (9,  7, 'Burger',              1),
    (10, 7, 'Menù',                2);

-- Le 25 voci. I nomi sono in maiuscolo/minuscolo normale: il maiuscolo del PDF lo applica il CSS.
INSERT INTO voci_menu (id, categoria_id, nome, descrizione, edizione, nota, posizione) VALUES
    -- Starters: prima gli Straccetti, che hanno i formati 5 pz e 10 pz, così l'intestazione
    -- delle colonne sta subito sopra di loro e non sembra riferita alle patatine (prezzo unico).
    (1,  1, 'Patatine stick',                 NULL, NULL, NULL, 2),
    (2,  1, 'Patatine stick bacon & cheese',  NULL, NULL, NULL, 3),
    (3,  1, 'Straccetti di pollo',            'Pollo croccante ricetta bro', NULL, NULL, 1),
    -- Salad
    (4,  2, 'Italian salad', 'Insalata, rucola, pollo alla griglia, pomodorini, scaglie di Parmigiano, crostini', NULL, NULL, 1),
    (5,  2, 'Rocket Salad',  'Insalata, rucola, pollo alla griglia, noci, speck, crostini', NULL, NULL, 2),
    -- Burger
    (6,  3, 'Smash Burger',             'Hamburger, insalata, pomodoro, salsa smash', NULL, NULL, 1),
    (7,  3, 'Smash Salad',              'Hamburger, insalata, pomodoro, cipolla, salsa smash', NULL, NULL, 2),
    (8,  3, 'Smash Cheeseburger',       'Hamburger, cheddar, salsa smash', NULL, NULL, 3),
    (9,  3, 'Smash Bacon Cheeseburger', 'Hamburger, cheddar, bacon, salsa smash', NULL, NULL, 4),
    (10, 3, 'Smash Onion Rings',        'Hamburger, cheddar, bacon, anelli di cipolla croccanti, salsa bbq', NULL, NULL, 5),
    (11, 3, 'Los Pollos Classic',       'Pollo croccante, insalata, salsa mayo', NULL, NULL, 6),
    (12, 3, 'Los Pollos Bacon',         'Pollo croccante, cheddar, bacon, salsa smash', NULL, NULL, 7),
    -- Kids Menù
    (13, 4, 'Menù Kids Smash Baby Hamburger', 'Bun con hamburger, patatine e soft drink', NULL, NULL, 1),
    (14, 4, 'Menù Kids Los Pollos',           'Bun con pollo impanato, patatine e soft drink', NULL, NULL, 2),
    -- Soft Drinks
    (15, 5, 'Acqua 50cl',                      NULL, NULL, NULL, 1),
    (16, 5, 'Coca Cola / Fanta / Sprite 33cl', NULL, NULL, NULL, 2),
    (17, 5, 'Red Bull 33cl',                   NULL, NULL, NULL, 3),
    -- Beers
    (18, 6, 'Nastro Azzurro 33cl', NULL, NULL, NULL, 1),
    (19, 6, 'Heineken 33cl',       NULL, NULL, NULL, 2),
    (20, 6, 'Tennent''s 33cl',     NULL, NULL, NULL, 3),
    -- The Originals
    (21, 7, 'Scarulella Bro', 'Hamburger 180gr, provola, scarola, salame a listarelle', 'Winter Edition', NULL, 1),
    (22, 7, 'Friariello Bro', 'Hamburger 180gr, provola e friarielli', 'Winter Edition', NULL, 2),
    (23, 7, 'Fungitiello',    'Hamburger 180gr, provola impanata, melanzane a funghetto', 'Summer Edition', NULL, 3),
    (24, 7, 'Scapece',        'Hamburger 180gr, zucchine alla scapece, prosciutto crudo', 'Summer Edition', NULL, 4),
    (25, 7, 'Veggy 2.0',      'Verdure di stagione, provola impanata, salsa mayo', NULL, 'Prova anche la variante con la zucca', 5);

-- Prezzi: (voce, formato, centesimi). Formato NULL = prezzo unico.
INSERT INTO prezzi_voce (voce_id, formato_id, prezzo_centesimi) VALUES
    -- Starters: Patatine stick 3,00 e 4,00 (unici); Straccetti 5 pz 4,00 · 10 pz 7,00
    (1, NULL, 300),
    (2, NULL, 400),
    (3, 1, 400), (3, 2, 700),
    -- Salad: Single · Menù
    (4, 3, 800), (4, 4, 1000),
    (5, 3, 800), (5, 4, 1000),
    -- Burger: Panino single · Panino double · Menù single · Menù double
    (6,  5, 700), (6,  6, 850), (6,  7, 1000), (6,  8, 1200),
    (7,  5, 750), (7,  6, 900), (7,  7, 1100), (7,  8, 1200),
    (8,  5, 700), (8,  6, 850), (8,  7, 1100), (8,  8, 1200),
    (9,  5, 750), (9,  6, 900), (9,  7, 1100), (9,  8, 1200),
    (10, 5, 800), (10, 6, 950), (10, 7, 1150), (10, 8, 1300),
    -- Los Pollos: solo i prezzi single
    (11, 5, 700), (11, 7, 1100),
    (12, 5, 750), (12, 7, 1100),
    -- Kids Menù
    (13, NULL, 600),
    (14, NULL, 600),
    -- Soft Drinks
    (15, NULL, 100),
    (16, NULL, 200),
    (17, NULL, 300),
    -- Beers
    (18, NULL, 250),
    (19, NULL, 300),
    (20, NULL, 350),
    -- The Originals: Burger · Menù
    (21, 9, 900), (21, 10, 1300),
    (22, 9, 900), (22, 10, 1300),
    (23, 9, 900), (23, 10, 1300),
    (24, 9, 900), (24, 10, 1300),
    (25, 9, 700), (25, 10, 1100);

COMMIT;
