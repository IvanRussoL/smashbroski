// Caricato nel <head>, prima che la pagina si disegni: la classe "js" c'è già al primo disegno,
// così sul telefono il pannello della navbar nasce chiuso. Aggiunta da navbar.js, a pagina già
// disegnata, faceva vedere per circa 300 ms le voci aperte che poi sfumavano (lampo del pannello).
// File esterno e non script in linea: la Content-Security-Policy accetta solo script-src 'self'.
document.documentElement.classList.add("js");
