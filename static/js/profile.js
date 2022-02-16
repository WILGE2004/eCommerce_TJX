import {Menu} from "./Menu.js"

let btn_save_pass = document.getElementById("save_pass");
let btn_save_img = document.getElementById("enviar");

btn_save_pass.addEventListener("click", update_pass)
btn_save_img.addEventListener("click", update_img)

function update_pass(){
    document.getElementById("form_my_profile").action="/perfil/update_pass"
}

function update_img(){
    document.getElementById("form_my_profile").action="/perfil/update_user_img"
}