import {Menu} from "./menu.js"

let btn_comprar = document.getElementById("btn_comprar");
let btn_deseos = document.getElementById("btn_deseos");
let btn_comentar = document.getElementById("btn_comentar");
let nombre_producto= document.getElementById("name_pd");

btn_comprar.addEventListener("click",Compra);
btn_deseos.addEventListener("click",Agregar);
btn_comentar.addEventListener("click", Comentar);

function Compra(){
    alert("Procesando...");
    var nameprod= nombre_producto.innerHTML ;
    document.getElementById("form_producto").action="/producto/"+nameprod+"/compra" ;
}

function Agregar(){
    alert("Procesando...");
    var nameprod= nombre_producto.innerHTML ;
    document.getElementById("form_producto").action="/producto/"+nameprod+"/lista" ;
}
function Comentar(){
    alert("Acción realizada");
}

export const Producto= {
    btn_comprar,
    btn_deseos,
    btn_comentar,
    nombre_producto,
    Compra,
    Agregar,
    Comentar
}