// Ferma le file di loghi dello sfondo mentre la pagina scorre e le fa ripartire poco dopo:
// sedici livelli in movimento durante lo scroll rendevano lo scorrimento del menù a scatti.
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
})();
