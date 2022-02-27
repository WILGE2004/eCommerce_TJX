import {Menu} from "./Menu.js"

let btn_user = document.getElementById("btn_user")
btn_user.addEventListener("click", create_user)


function create_user() {
    document.getElementById("info").action="/dashboard/registro/user"
}