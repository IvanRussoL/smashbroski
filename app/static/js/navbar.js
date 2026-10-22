// Pulsante con le tre linee della navbar: apre e chiude le voci di navigazione sui telefoni.
// Senza JavaScript il pulsante non compare e le voci restano visibili nella barra.
(function () {
    const navbar = document.querySelector(".navbar");
    const pulsante = document.querySelector(".navbar-pulsante");
    const voci = document.getElementById("navbar-voci");
    if (!navbar || !pulsante || !voci) {
        return;
    }
    // La classe "js" mostra il pulsante e trasforma le voci in un pannello a scomparsa (stile.css).
    document.documentElement.classList.add("js");

    function aperto() {
        return pulsante.getAttribute("aria-expanded") === "true";
    }

    function imposta(apri) {
        pulsante.setAttribute("aria-expanded", String(apri));
        navbar.classList.toggle("navbar-aperta", apri);
    }

    pulsante.addEventListener("click", function () {
        imposta(!aperto());
    });

    // Esc chiude il pannello e riporta il focus sul pulsante.
    document.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape" && aperto()) {
            imposta(false);
            pulsante.focus();
        }
    });

    // Un clic su una voce o fuori dalla navbar chiude il pannello.
    voci.addEventListener("click", function (evento) {
        if (evento.target.closest("a")) {
            imposta(false);
        }
    });
    document.addEventListener("click", function (evento) {
        if (aperto() && !navbar.contains(evento.target)) {
            imposta(false);
        }
    });

    // Passando a uno schermo largo (telefono ruotato, finestra allargata) le voci tornano nella barra.
    // Nel passaggio (anche con lo zoom Ctrl +/- del computer) le animazioni del pannello sono spente
    // per un attimo, altrimenti le voci "volano" via o entrano come se si aprisse il menù.
    let attesa = null;
    window.matchMedia("(min-width: 900px)").addEventListener("change", function () {
        document.documentElement.classList.add("senza-animazioni");
        imposta(false);
        clearTimeout(attesa);
        attesa = setTimeout(function () {
            document.documentElement.classList.remove("senza-animazioni");
        }, 400);
    });
})();

// Ora di Pompei nella navbar, con il sole di giorno e la luna dopo il tramonto (come Habita79).
// L'ora è quella del locale (fuso delle impostazioni), non quella del visitatore; si aggiorna
// allo scoccare di ogni minuto. Senza JavaScript l'elemento resta nascosto.
(function () {
    const orologio = document.querySelector(".navbar-ora");
    if (!orologio) {
        return;
    }
    const valore = orologio.querySelector(".navbar-ora-valore");
    const formato = new Intl.DateTimeFormat("it-IT", {
        timeZone: orologio.dataset.fuso || "Europe/Rome",
        hour: "2-digit",
        minute: "2-digit",
    });

    // Coordinate di Pompei, per calcolare alba e tramonto.
    const LATITUDINE = 40.75;
    const LONGITUDINE = 14.5;
    const GRADI = Math.PI / 180;

    // true se il sole è sopra l'orizzonte. Formula semplificata dell'alba e del tramonto
    // (declinazione del sole ed equazione del tempo): sbaglia al massimo di qualche minuto,
    // abbastanza per scegliere un'icona. Calcolo in UTC, quindi l'ora legale non conta.
    function eGiorno(adesso) {
        const inizioAnno = Date.UTC(adesso.getUTCFullYear(), 0, 1);
        const giorno = Math.floor((adesso.getTime() - inizioAnno) / 86400000) + 1;
        const declinazione = -23.44 * GRADI * Math.cos((2 * Math.PI / 365) * (giorno + 10));
        const latitudine = LATITUDINE * GRADI;
        const cosAngolo = (Math.sin(-0.833 * GRADI) - Math.sin(latitudine) * Math.sin(declinazione))
            / (Math.cos(latitudine) * Math.cos(declinazione));
        const angolo = Math.acos(Math.min(1, Math.max(-1, cosAngolo))) / GRADI;
        const b = (2 * Math.PI * (giorno - 81)) / 364;
        const equazioneDelTempo = 9.87 * Math.sin(2 * b) - 7.53 * Math.cos(b) - 1.5 * Math.sin(b);
        const mezzogiorno = 720 - 4 * LONGITUDINE - equazioneDelTempo; // minuti dalla mezzanotte UTC
        const minuti = adesso.getUTCHours() * 60 + adesso.getUTCMinutes();
        return minuti >= mezzogiorno - 4 * angolo && minuti < mezzogiorno + 4 * angolo;
    }

    function aggiorna() {
        const adesso = new Date();
        valore.textContent = formato.format(adesso);
        orologio.classList.toggle("notte", !eGiorno(adesso));
    }

    function prossimoMinuto() {
        aggiorna();
        setTimeout(prossimoMinuto, 60000 - (Date.now() % 60000) + 50);
    }

    orologio.hidden = false;
    prossimoMinuto();
    // Tornando sulla scheda dopo un po' (telefono in standby) l'ora si aggiorna subito.
    document.addEventListener("visibilitychange", function () {
        if (!document.hidden) {
            aggiorna();
        }
    });
})();
