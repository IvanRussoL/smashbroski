// Indice delle categorie del menù: evidenzia (aria-current) la categoria che si sta guardando,
// sia dopo un tocco sulla pillola sia scorrendo la pagina. All'apertura è attiva la prima.
// Senza JavaScript l'indice funziona lo stesso, solo senza evidenziazione.
(function () {
    const indice = document.getElementById("indice");
    if (!indice) {
        return;
    }
    const link = Array.from(indice.querySelectorAll("a[href^='#']"));
    const voci = link
        .map(function (a) {
            const titolo = document.getElementById(a.getAttribute("href").slice(1));
            return titolo ? { link: a, blocco: titolo.closest("section") || titolo } : null;
        })
        .filter(Boolean);
    if (voci.length === 0) {
        return;
    }
    const movimentoRidotto = window.matchMedia("(prefers-reduced-motion: reduce)");
    let attiva = null;
    let scelta = null; // ultima pillola toccata
    let inAttesa = false;

    function evidenzia(voce) {
        if (voce === attiva) {
            return;
        }
        if (attiva) {
            attiva.link.removeAttribute("aria-current");
        }
        attiva = voce;
        voce.link.setAttribute("aria-current", "location");
        // Su telefono l'indice scorre in orizzontale: la pillola attiva resta in vista.
        const sinistra = voce.link.offsetLeft;
        const destra = sinistra + voce.link.offsetWidth;
        if (sinistra < indice.scrollLeft || destra > indice.scrollLeft + indice.clientWidth) {
            indice.scrollTo({ left: sinistra - 12, behavior: movimentoRidotto.matches ? "auto" : "smooth" });
        }
    }

    function aggiorna() {
        inAttesa = false;
        // La categoria cambia quando la successiva arriva al 40% dello spazio sotto le pillole,
        // cioè quando occupa già la parte alta dello schermo (con la linea subito sotto le pillole
        // il cambio arrivava troppo tardi, a categoria nuova quasi tutta in vista).
        const sottoPillole = indice.getBoundingClientRect().bottom;
        const linea = sottoPillole + (window.innerHeight - sottoPillole) * 0.4;
        let migliore = voci[0];
        let altezzaMigliore = -Infinity;
        voci.forEach(function (voce) {
            const alto = voce.blocco.getBoundingClientRect().top;
            if (alto <= linea && alto > altezzaMigliore + 4) {
                migliore = voce;
                altezzaMigliore = alto;
            }
        });
        // Dopo un tocco resta attiva la pillola toccata finché il suo blocco è dove è atterrato,
        // subito sotto le pillole: un blocco corto non lascia il posto a quello che lo segue.
        if (scelta) {
            const altoScelta = scelta.blocco.getBoundingClientRect().top;
            if (altoScelta >= sottoPillole - 8 && altoScelta <= sottoPillole + 48) {
                migliore = scelta;
            } else {
                scelta = null;
            }
        }
        evidenzia(migliore);
    }

    function programma() {
        if (!inAttesa) {
            inAttesa = true;
            window.requestAnimationFrame(aggiorna);
        }
    }

    voci.forEach(function (voce) {
        voce.link.addEventListener("click", function () {
            scelta = voce;
            evidenzia(voce);
        });
    });
    window.addEventListener("scroll", programma, { passive: true });
    window.addEventListener("resize", programma);
    aggiorna();
})();
