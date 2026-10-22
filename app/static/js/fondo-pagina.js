// Safari su iPhone (iOS 26) colora lo spazio sotto la sua barra "a vetro" con il fondo della
// pagina. Quando il footer rosso entra nello schermo il fondo diventa rosso, così in basso non
// resta una riga del colore di cima (blu in home, crema nelle altre pagine).
(function () {
    const footer = document.querySelector(".footer");
    if (!footer || !("IntersectionObserver" in window)) {
        return;
    }
    const radice = document.documentElement;
    new IntersectionObserver(function (voci) {
        radice.classList.toggle("al-footer", voci[0].isIntersecting);
    }).observe(footer);
})();
