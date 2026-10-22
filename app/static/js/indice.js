// Indice delle categorie del menù: evidenzia (aria-current) la categoria che si sta guardando,
// sia dopo un tocco sulla pillola sia scorrendo la pagina. All'apertura è attiva la prima.
// Su desktop, scorrendo, si accendono insieme le categorie affiancate (es. Starters e Salad).
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
    let attive = [];
    let scelta = null; // ultima pillola toccata
    let inAttesa = false;

    // gruppo: la categoria principale per prima, poi quelle affiancate.
    function evidenzia(gruppo) {
        if (gruppo.length === attive.length && gruppo.every(function (v, i) { return v === attive[i]; })) {
            return;
        }
        attive.forEach(function (v) {
            v.link.removeAttribute("aria-current");
        });
        attive = gruppo;
        gruppo.forEach(function (v) {
            v.link.setAttribute("aria-current", "location");
        });
        // Su telefono l'indice scorre in orizzontale: la pillola attiva resta in vista.
        const voce = gruppo[0];
        const sinistra = voce.link.offsetLeft;
        const destra = sinistra + voce.link.offsetWidth;
        if (sinistra < indice.scrollLeft || destra > indice.scrollLeft + indice.clientWidth) {
            indice.scrollTo({ left: sinistra - 12, behavior: movimentoRidotto.matches ? "auto" : "smooth" });
        }
    }

    // Categorie in un'altra colonna accanto alla principale (Salad accanto a Starters, The Originals
    // accanto a Kids, Soft Drinks e Beers): su telefono c'è una colonna sola e il gruppo resta di una.
    function affiancate(principale, linea) {
        const r = principale.blocco.getBoundingClientRect();
        return voci.filter(function (voce) {
            if (voce === principale) {
                return false;
            }
            const altro = voce.blocco.getBoundingClientRect();
            const altraColonna = altro.left >= r.right || altro.right <= r.left;
            const stessaAltezza = altro.top < r.bottom && altro.bottom > r.top;
            return altraColonna && stessaAltezza && altro.top <= linea;
        });
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
                evidenzia([scelta]); // dopo un tocco si accende solo la pillola toccata
                return;
            }
            scelta = null;
        }
        evidenzia([migliore].concat(affiancate(migliore, linea)));
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
            evidenzia([voce]);
        });
    });
    window.addEventListener("scroll", programma, { passive: true });
    window.addEventListener("resize", programma);
    aggiorna();
})();
