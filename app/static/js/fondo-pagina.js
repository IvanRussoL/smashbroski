// Safari su iPhone (iOS 26) colora lo spazio sotto la sua barra "a vetro" con il fondo della
// pagina. Quando il footer rosso entra nello schermo il fondo diventa rosso, così in basso non
// resta una riga del colore di cima (blu in home, crema nelle altre pagine).
// Safari però prende il colore anche dagli elementi fissi che toccano il bordo dello schermo:
// su Menù e Orari e contatti lo sfondo di loghi (crema) copriva il rosso. Finché il footer è
// sullo schermo lo sfondo di loghi finisce dove cominciano le fasce del footer, che comunque
// lo nascondono, e non tocca più il bordo in basso.
(function () {
    const footer = document.querySelector(".footer");
    if (!footer || !("IntersectionObserver" in window)) {
        return;
    }
    const radice = document.documentElement;
    const sfondo = document.querySelector(".sfondo-loghi");
    const inizioFooter = document.querySelector(".footer-dove") || footer;
    let alFooter = false;
    let inAttesa = false;

    function tagliaSfondo() {
        inAttesa = false;
        const taglio = Math.max(0, window.innerHeight - inizioFooter.getBoundingClientRect().top);
        radice.style.setProperty("--taglio-sfondo", taglio + "px");
    }

    function alloScroll() {
        if (alFooter && !inAttesa) {
            inAttesa = true;
            requestAnimationFrame(tagliaSfondo);
        }
    }

    new IntersectionObserver(function (voci) {
        alFooter = voci[0].isIntersecting;
        radice.classList.toggle("al-footer", alFooter);
        if (sfondo && alFooter) {
            tagliaSfondo();
        }
    }).observe(footer);

    if (sfondo) {
        window.addEventListener("scroll", alloScroll, { passive: true });
        window.addEventListener("resize", alloScroll);
    }
})();
