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
    let scelta = null; // ultima pillola toccata: vince sui blocchi alla stessa altezza (Starters e Salad su desktop)
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
        // Linea appena sotto le pillole: è attivo il blocco più in basso che l'ha già raggiunta.
        const linea = indice.getBoundingClientRect().bottom + 24;
        let migliore = voci[0];
        let altezzaMigliore = -Infinity;
        voci.forEach(function (voce) {
            const alto = voce.blocco.getBoundingClientRect().top;
            if (alto <= linea && alto > altezzaMigliore + 4) {
                migliore = voce;
                altezzaMigliore = alto;
            }
        });
        if (scelta && Math.abs(scelta.blocco.getBoundingClientRect().top - altezzaMigliore) <= 4) {
            migliore = scelta;
        } else {
            scelta = null;
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
