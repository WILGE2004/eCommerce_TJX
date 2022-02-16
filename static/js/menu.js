let btn_menu = document.getElementById("btn_menu");
let nav = document.getElementById("nav");

btn_menu.addEventListener("click", Mostrar);

function Mostrar() {
    nav.classList.toggle("cMostrar");
}

export const Menu = {
    btn_menu,
    nav,
    Mostrar
}