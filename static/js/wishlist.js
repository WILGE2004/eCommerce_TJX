import {Menu} from "./menu.js"

let btn_comprar = document.getElementById("btn_comprar");
let btn_eliminar = document.getElementById("btn_borrar");
let nombre_producto= document.getElementById("name_pd");

btn_comprar.addEventListener("click",Compra)
btn_eliminar.addEventListener("click",Borra)

function Compra(){
    alert("Procesando...");
    var nameprod= nombre_producto.innerHTML ;
    document.getElementById("form_deseos").action="/producto/"+nameprod+"/compra" ;
}
function Borra(){
    alert("Procesando...");
    var nameprod= nombre_producto.innerHTML ;
    document.getElementById("form_deseos").action="/delet_list/"+nameprod ;
}