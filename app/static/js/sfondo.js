// Ferma le file di loghi dello sfondo mentre la pagina scorre e le fa ripartire poco dopo:
// sedici livelli in movimento durante lo scroll rendevano lo scorrimento del menù a scatti.
// Durante lo zoom con due dita (e finché la pagina resta ingrandita) le file perdono anche
// l'animazione: senza i loro sedici livelli il telefono ridisegna la pagina più in fretta e non
// restano per un attimo zone vuote (succedeva su Chrome per Android rimpicciolendo veloce).
(function () {
    const radice = document.documentElement;
    let attesa = null;
    window.addEventListener("scroll", function () {
        if (attesa === null) {
            radice.classList.add("scorrendo");
        } else {
            clearTimeout(attesa);
        }
        attesa = setTimeout(function () {
            radice.classList.remove("scorrendo");
            attesa = null;
        }, 200);
    }, { passive: true });

    const vista = window.visualViewport;
    if (!vista) {
        return;
    }
    let attesaZoom = null;
    vista.addEventListener("resize", function () {
        radice.classList.add("zoom");
        clearTimeout(attesaZoom);
        attesaZoom = setTimeout(function () {
            // Riparte solo quando la pagina è tornata alla grandezza normale.
            if (vista.scale <= 1.01) {
                radice.classList.remove("zoom");
            }
        }, 400);
    });
})();
