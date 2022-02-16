from flask import Flask, render_template, request, redirect, url_for, session, flash
from markupsafe import escape
import os
import sqlite3
from sqlite3 import Error

import hashlib
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import re

def valid_email(email):
    expresion_regular = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    return re.match(expresion_regular, email) is not None

def valid_pass(password):
    expresion_regular = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
    if re.search(expresion_regular, password):
        return True
    else:
        return False

app = Flask(__name__)
app.secret_key=os.urandom(24)

@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        if 'user' in session:
            try:
                with sqlite3.connect("TJX_productos.db") as con:
                    cur = con.cursor()
                    query = cur.execute("SELECT Rol FROM Usuarios WHERE Correo = ?",[session['user']]).fetchone()
                    rol = query
                    if rol[0] == 'Admin':
                        con.row_factory = sqlite3.Row
                        cur = con.cursor()
                        query = cur.execute('SELECT Nombre, Descripcion, URL_prod FROM Productos WHERE Precio < 20000')
                        if query is None:
                            error = 'No hay productos Destacados'
                            flash(error)
                            return render_template('MisCompras.html')
                        return render_template('Index_admin.html', row = query)
                    else:
                        con.row_factory = sqlite3.Row
                        cur = con.cursor()
                        query = cur.execute('SELECT Nombre, Descripcion, URL_prod FROM Productos WHERE Precio < 20000')
                        if query is None:
                            error = 'No hay productos Destacados'
                            flash(error)
                            return render_template('MisCompras.html')
                        return render_template('Index.html', row = query)
            except Error:
                return redirect('/')
        else:
            try:
                with sqlite3.connect('TJX_productos.db') as con:
                            con.row_factory = sqlite3.Row
                            cur = con.cursor()
                            query = cur.execute('SELECT Nombre, Descripcion, URL_prod FROM Productos WHERE Precio < 20000')
                            if query is None:
                                error = 'No hay productos Destacados'
                                flash(error)
                                return render_template('MisCompras.html')
                            return render_template('Index.html', row = query)
            except Error:
                print(Error)            

@app.route('/compras', methods=['GET'])
def compra():
    if 'user' in session:
        try:
            with sqlite3.connect('TJX_productos.db') as con:
                        con.row_factory = sqlite3.Row
                        cur = con.cursor()
                        query = cur.execute('SELECT Nom_producto, Descripcion, URL_prod FROM Mis_compras WHERE Usuario = ?', [session['user']])
                        if query is None:
                            error = 'No tiene productos'
                            flash(error)
                            return render_template('MisCompras.html')
                        return render_template('MisCompras.html', row = query)
        
        except Error:
            print(Error)
    else:
        error = 'Por favor Inicie Sesion'
        flash(error)
        return render_template('MisCompras.html')
        #return redirect('/login')
        #return "<a href='/login'>Por favor Inicie Sesión</a>"

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user' in session:
        try:
            with sqlite3.connect("TJX_productos.db") as con:
                cur = con.cursor()
                query = cur.execute("SELECT Rol FROM Usuarios WHERE Correo = ?",[session['user']]).fetchone()
                rol = query
                if rol[0] == 'Admin':
                    return render_template('DashBoard.html')
                else:
                    return redirect('/')
        except Error:
            print(Error)
            return redirect('/')
    else:
        return redirect('/')

@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
        session.clear()
        flash('Sesión cerrada exitosamente!')
        return redirect('/login')
    else:
        flash("Primero debe iniciar sesion")
        return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        user = escape(request.form['email'])
        password = escape(request.form['password'])
        try:
            with sqlite3.connect("TJX_productos.db") as con:
                cur = con.cursor()
                query=cur.execute("SELECT Contraseña FROM Usuarios WHERE Correo=?",[user]).fetchone()
                if query!=None:
                    if check_password_hash(query[0],password):
                        session['user']=user
                        return redirect("/")
                    else:
                        flash("Credenciales incorrectas")
                        return redirect('/login')
                else:
                    flash("El usuario no existe")
                    return redirect('/login')
        except Error:
            flash("Algo salió mal: "+Error)
            return redirect('/login')

    if 'user' in session:
        return redirect('/perfil')
    else:
        return render_template('login.html')

@app.route('/registrarse', methods=['GET','POST'])
def registrarse():
    if request.method == 'POST':
        email = escape(request.form['email'])
        name = escape(request.form['name'])
        phone = escape(request.form['phone'])
        password = escape(request.form['password'])
        check_pass = escape(request.form['check_pass'])
        conditions = escape(request.form.get('conditions'))
        rol = "Final_user"

        if conditions == "None":
            flash("Debe aceptar los terminos y condiciones")
            return redirect('/registrarse')
        else:
            if len(email)==0 or len(name)==0 or len(phone)==0 or len(password)==0 or len(check_pass)==0:
                flash("Algunos campos obligatorios están vacíos, trate de nuevo")
                return redirect('/registrarse')
            else:
                if not valid_email(email):
                    flash("Ingrese un correo valido")
                    return redirect('/registrarse')
                else:
                    if not valid_pass(password):
                        flash("La contraseña debe contener minimo 8 caracteres, entre ellos: numeros, letras (mayus y min) y un caracter especial")
                        return redirect('/registrarse')
                    else:
                        if password != check_pass:
                            flash("Las contraseñas no coiciden")
                            return redirect('/registrarse')
                        else:
                            hash_clave=generate_password_hash(password)
                            try:
                                with sqlite3.connect("TJX_productos.db") as con:
                                    cur = con.cursor()
                                    cur.execute("INSERT INTO Usuarios(Correo,Nombre,Rol,Telefono,Contraseña) VALUES (?,?,?,?,?)",(email,name,rol,phone,hash_clave))
                                    con.commit()
                                    flash("Registro exitoso, ahora puede iniciar sesión")
                                    return redirect("/")
                                
                            except Error:
                                flash("Algo salió mal: "+Error)
                                return redirect("/registrarse")

    if 'user' in session:
        return redirect('/')
    else:
        return render_template('signup.html')

@app.route('/dashboard/registro', methods=['GET','POST'])
def registro_admin():
    if 'user' in session:
        try:
            with sqlite3.connect("TJX_productos.db") as con:
                cur = con.cursor()
                query = cur.execute("SELECT Rol FROM Usuarios WHERE Correo = ?",[session['user']]).fetchone()
                rol = query
                if rol[0] == 'Admin':
                    if request.method =="GET":
                        return render_template('signup_admin.html')

                    if request.method == 'POST':
                        email = escape(request.form['email'])
                        name = escape(request.form['name'])
                        phone = escape(request.form['phone'])
                        password = escape(request.form['password'])
                        check_pass = escape(request.form['check_pass'])
                        rol = "Admin"

                        if len(email)==0 or len(name)==0 or len(phone)==0 or len(password)==0 or len(check_pass)==0:
                            flash("Algunos campos obligatorios están vacíos, trate de nuevo")
                            return redirect('/dashboard/registro')
                        else:
                            if not valid_email(email):
                                flash("Ingrese un correo valido")
                                return redirect('/dashboard/registro')
                            else:
                                if not valid_pass(password):
                                    flash("La contraseña debe contener minimo 8 caracteres, entre ellos: numeros, letras (mayus y min) y un caracter especial")
                                    return redirect('/dashboard/registro')
                                else:
                                    if password != check_pass:
                                        flash("Las contraseñas no coiciden")
                                        return redirect('/dashboard/registro')
                                    else:
                                        hash_clave=generate_password_hash(password)
                                        try:
                                                cur = con.cursor()
                                                cur.execute("INSERT INTO Usuarios(Correo,Nombre,Rol,Telefono,Contraseña) VALUES (?,?,?,?,?)",(email,name,rol,phone,hash_clave))
                                                con.commit()
                                                flash("Registro exitoso, nuevo usuario creado")
                                                return redirect("/dashboard")
                                            
                                        except Error:
                                            flash("Algo salió mal: "+Error)
                                            return redirect("/dashboard/registro")                    
                else:
                    return redirect('/')
        except Error:
            print(Error)
            return redirect('/')
    else:
        return redirect('/')

@app.route('/dashboard/registro/user',methods=['POST'])
def registro_us():
    if request.method == 'POST':
        email = escape(request.form['email'])
        name = escape(request.form['name'])
        phone = escape(request.form['phone'])
        password = escape(request.form['password'])
        check_pass = escape(request.form['check_pass'])
        rol = "Final_user"

        if len(email)==0 or len(name)==0 or len(phone)==0 or len(password)==0 or len(check_pass)==0:
            flash("Algunos campos obligatorios están vacíos, trate de nuevo")
            return redirect('/dashboard/registro')
        else:
            if not valid_email(email):
                flash("Ingrese un correo valido")
                return redirect('/dashboard/registro')
            else:
                if not valid_pass(password):
                    flash("La contraseña debe contener minimo 8 caracteres, entre ellos: numeros, letras (mayus y min) y un caracter especial")
                    return redirect('/dashboard/registro')
                else:
                    if password != check_pass:
                        flash("Las contraseñas no coiciden")
                        return redirect('/dashboard/registro')
                    else:
                        hash_clave=generate_password_hash(password)
                        try:
                            with sqlite3.connect("TJX_productos.db") as con:
                                cur = con.cursor()
                                cur.execute("INSERT INTO Usuarios(Correo,Nombre,Rol,Telefono,Contraseña) VALUES (?,?,?,?,?)",(email,name,rol,phone,hash_clave))
                                con.commit()
                                flash("Registro exitoso, nuevo usuario creado")
                                return redirect("/dashboard")
                            
                        except Error:
                            flash("Algo salió mal: "+Error)
                            return redirect("/dashboard/registro")

    if 'user' in session:
        return redirect('/')
    else:
        return render_template('signup_admin.html')

@app.route('/dashboard/eliminar_usuario', methods= ['GET', 'POST'])
def eliminar_usuario():
    if 'user' in session:
        if request.method == 'GET':
            with sqlite3.connect("TJX_productos.db") as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM Usuarios')
                data=cur.fetchall()
                return render_template('eliminar_usuario.html', data = data)

        if request.method == 'POST':
            usuario = escape(request.form['usuario'])
            try:
                with sqlite3.connect("TJX_productos.db") as con:
                    cur = con.cursor()
                    query = cur.execute("SELECT Rol FROM Usuarios WHERE Correo = ?",[session['user']]).fetchone()
                    rol = query
                    if rol[0] == 'Admin':
                            try:
                                buscar = cur.execute("SELECT * FROM Usuarios WHERE Correo = ?",[usuario]).fetchone()
                                if buscar is None:
                                    flash('Error... Usuario NO existe')
                                    return render_template('eliminar_usuario.html')
                                else:
                                    cur.execute("DELETE FROM Usuarios WHERE Correo = ?",[usuario])
                                    con.commit()
                                    flash('Usuario eliminado Exitosamente')
                                    return render_template('eliminar_usuario.html')
                            except Error:
                                flash('Error... No se pudó eliminar el Usuario')
                                return render_template('eliminar_usuario.html')
                    else:
                        return redirect('/')
            except Error:
                print(Error)
                return redirect('/')
    else:
        return redirect('/')

@app.route('/perfil', methods=['GET','POST'])
def perfil():
    if 'user' in session:
        if request.method == 'POST':
                name = escape(request.form['name'])
                phone = escape(request.form['phone'])
                if len(name)==0 or len(phone)==0:
                    flash("Algunos campos están vacíos")
                    return redirect('/perfil')
                else:
                    try:
                        with sqlite3.connect("TJX_productos.db") as con:
                            cur = con.cursor()
                            cur.execute("UPDATE Usuarios SET Nombre=?, Telefono=? WHERE Correo=?",[name, phone, session['user']])
                            con.commit()
                            if con.total_changes > 0:
                                flash("Datos actualizados con exito!!")
                                return redirect("/perfil")
                            else:
                                flash("No se pudo actualizar la información")
                                return redirect('/perfil')
                    except Error:
                        flash("Algo salió mal "+Error)
                        return redirect('/perfil')       

        if request.method == 'GET':
                try:
                    with sqlite3.connect("TJX_productos.db") as con:
                        con.row_factory = sqlite3.Row
                        cur = con.cursor()
                        query=cur.execute("SELECT Nombre, Telefono, URL_img FROM Usuarios WHERE Correo=?",[session['user']]).fetchone()
                        
                        if query is None:
                            flash("El usuario no existe")
                            return redirect('/')
                except Error:
                    flash("Algo salió mal "+Error)
                    return redirect('/perfil')
                
                if query[2]== None:
                    url = "/static/img/user.png"
                else:
                    url= '/static/img/img_users/'+query[2]
                return render_template('my_profile.html',path_img=url,name=query[0],phone=query[1],email=session['user'])
    else:
        flash("Por favor inicie sesión")
        return redirect('/login')
    
@app.route('/perfil/update_pass', methods=['POST'])
def update_pass():
    if 'user' in session:
        old      = escape(request.form['old_pass'])
        new_pass = escape(request.form['new_pass'])
        check    = escape(request.form['check_pass'])
        try:
            with sqlite3.connect("TJX_productos.db") as con:
                cur = con.cursor()
                query=cur.execute("SELECT Contraseña FROM Usuarios WHERE Correo=?",[session['user']]).fetchone()
                if query!=None:
                    if check_password_hash(query[0],old):
                        if not valid_pass(new_pass):
                            flash("La contraseña debe contener minimo 8 caracteres, entre ellos: numeros, letras (mayus y min) y un caracter especial")
                            return redirect('/perfil')
                        else:
                            if new_pass == check:
                                hash_clave = generate_password_hash(new_pass)
                                cur.execute("UPDATE Usuarios SET Contraseña=? WHERE Correo=?",[hash_clave, session['user']])
                                con.commit()
                                if con.total_changes > 0:
                                    flash("Datos actualizados con exito")
                                    return redirect('/perfil')
                                else:
                                    flash("No se pudo actualizar la información")
                                    return redirect('/perfil')
                            else:
                                flash("Las contraseñas no coinciden")
                                return redirect('/perfil')
                    else:
                        flash("Credenciales incorrectas, ingrese su contraseña actual")
                        return redirect('/perfil')
                else:
                    flash("El usuario no existe")
                    return redirect('/perfil')
        except Error:
            flash("Algo salió mal"+Error)
            return redirect('/perfil')
    else:
        flash("Por favor inicie sesión")
        return redirect('/login')       

@app.route('/perfil/update_user_img', methods=['POST'])
def update_img():
    if 'user' in session:
        f = request.files['archivo']
        filename = secure_filename(f.filename) 
        try:
            app.config['UPLOAD_FOLDER'] = './static/img/img_users'
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            try:
                with sqlite3.connect("TJX_productos.db") as con:
                    cur = con.cursor()
                    cur.execute("UPDATE Usuarios SET URL_img=? WHERE Correo=?",[filename, session['user']])
                    con.commit()
                    if con.total_changes > 0:
                        flash("Archivo subido exitosamente")
                        return redirect('/perfil')
                    else:
                        flash("No se pudo actualizar la información")
                        return redirect('/perfil')
            except Error:
                flash("Algo salió mal"+Error)
                return redirect('/perfil')
        except:
            flash("ERROR NO SELECCIONÓ NIGUNA IMAGEN")
            return redirect('/perfil')
    else:
        flash("Por favor inicie sesión")
        return redirect('/login') 
    
@app.route('/producto/<NombrePd>', methods=['GET','POST'])
def producto(NombrePd):
    nombre_prod= NombrePd+""
    if request.method=='POST':
        if 'user' in session:
            comentario=escape(request.form["mi_comentario"])
            rate=escape(request.form["calificacion"])
            if rate=="":
                flash("Para hacer el comentario, debe darle una calificación al producto.")
                return redirect('/producto/'+nombre_prod)
            else:
                try:
                    with sqlite3.connect("TJX_productos.db") as con:
                        cur = con.cursor()
                        consulta=cur.execute("SELECT Codigo FROM Productos WHERE Nombre=?",[nombre_prod]).fetchone()
                        cod_prod=consulta[0]
                        cur.execute("INSERT INTO Comentarios (Cod_producto, Usuario, Comentario,Calificacion) VALUES (?,?,?,?)",[cod_prod,session['user'],comentario, rate])
                        con.commit()
                except Error:
                    flash("No se pudo realizar el comentario, inténtelo más tarde")
                    return redirect('/')
        else:
            flash("Para hacer un comentario en el producto. Por favor inicie sesión.")
            return redirect('/login')
    
    if request.method=='GET':
        try:
            with sqlite3.connect("TJX_productos.db") as con:
                con.row_factory=sqlite3.Row
                cur = con.cursor()
                consulta=cur.execute("SELECT Codigo, Descripcion, Precio, URL_prod FROM Productos WHERE Nombre=?",[nombre_prod]).fetchone()
                if consulta is None:
                    flash("El producto no existe")
                    return redirect('/')
                cod_prod=consulta[0]
                descripcion=consulta[1]
                precio=consulta[2]
                if consulta[3] == None:
                    url="/static/img/paquete.png"
                else:
                    url="/static/img/img_products/"+consulta[3]  
                row = cur.execute("SELECT Usuario, Comentario, Calificacion FROM Comentarios WHERE Cod_producto=?",[cod_prod]).fetchall()
                promedio = cur.execute("SELECT AVG (Calificacion) FROM Comentarios WHERE Cod_producto=?",[cod_prod]).fetchone()
                if row != None:
                    return render_template("Producto.html",Nombre=nombre_prod,path_img=url,Descripcion=descripcion,Precio=precio,Rate=promedio[0],Usuario="Usuario",row=row)
                else:
                    return render_template("Producto.html",Nombre=nombre_prod,path_img=url,Descripcion=descripcion,Precio=precio,Rate=0,Usuario="Usuario")
                    
        except Error:
            flash("El producto no existe"+Error)
            return redirect('/')
    
    return redirect('/producto/'+nombre_prod)

@app.route('/producto/<NombrePd>/compra', methods=['POST'])
def compra_producto(NombrePd):
    if request.method=='POST':
        if 'user' in session:
            nombre_prod = NombrePd+""
            try:
                with sqlite3.connect("TJX_productos.db") as con:
                    con.row_factory=sqlite3.Row
                    cur = con.cursor()
                    consulta=cur.execute("SELECT Codigo, Descripcion, URL_prod FROM Productos WHERE Nombre=?",[nombre_prod]).fetchone()
                    cod_prod=consulta[0]
                    descripcion=consulta[1]
                    if consulta[2] == None:
                        url="/static/img/paquete.png"
                    else:
                        url="/static/img/img_products/"+consulta[2] 
                    if consulta != None:
                        cur.execute("INSERT INTO Mis_compras (Usuario, Cod_producto, Nom_producto, Descripcion, URL_prod) VALUES (?,?,?,?,?)",[session['user'],cod_prod,nombre_prod,descripcion, url])
                        con.commit()
            except Error:
                flash("No se realizó la compra")
                return redirect('/producto/'+nombre_prod)
        else:
            flash("Para hacer la compra del producto. Por favor inicie sesión.")
            return redirect('/login')
    
    return redirect('/producto/'+nombre_prod)

@app.route('/producto/<NombrePd>/lista', methods=['POST'])
def deseo_producto(NombrePd):
    if request.method=='POST':
        if 'user' in session:
            nombre_prod = NombrePd+""
            try:
                with sqlite3.connect("TJX_productos.db") as con:
                    con.row_factory=sqlite3.Row
                    cur = con.cursor()
                    consult2=cur.execute("SELECT Codigo, Descripcion, Precio, URL_prod FROM Productos WHERE Nombre=?",[nombre_prod]).fetchone()
                    cod_prod=consult2[0]
                    descripcion=consult2[1]
                    precio=consult2[2]
                    if consult2[3] == None:
                        url="/static/img/paquete.png"
                    else:
                        url="/static/img/img_products/"+consult2[3]
                    if consult2 != None:
                        cur.execute("INSERT INTO Wishlist (Usuario, Cod_producto, Nombre, Descripcion, Precio, URL_prod) VALUES (?,?,?,?,?,?)",[session['user'],cod_prod,nombre_prod,descripcion,precio,url])
                        con.commit()
                        flash("Se adicionó el producto a su lista de deseos")
                        return redirect('/producto/'+nombre_prod)
            except Error:
                flash("No se realizó la adición a la Wishlist porque ya se agregó a su Lista de Deseos")
                return redirect('/producto/'+nombre_prod)
        else:
            flash("Para hacer la adición a la Lista de Deseos. Por favor inicie sesión")
            return redirect('/login')
    
    return redirect('/producto/'+nombre_prod)

@app.route('/miscomentarios/<NombrePd>', methods=['GET','POST'])
def miscomentarios(NombrePd):
    if 'user' in session:
        nombre_prod=NombrePd+""
        if request.method=='GET':
            try:
                with sqlite3.connect("TJX_productos.db") as con:
                    con.row_factory=sqlite3.Row
                    cur = con.cursor()
                    consulta=cur.execute("SELECT Codigo, Descripcion, Precio, URL_prod FROM Productos WHERE Nombre=?",[nombre_prod]).fetchone()
                    if consulta is None:
                        flash("El producto no existe")
                        return redirect('/')
                    cod_prod=consulta[0]
                    descripcion=consulta[1]
                    precio=consulta[2]
                    if consulta[3] == None:
                        url="/static/img/paquete.png"
                    else:
                        url="/static/img/img_products/"+consulta[3]
                    row = cur.execute("SELECT Usuario, Comentario, Calificacion FROM Comentarios WHERE Usuario=? AND Cod_producto=?",[session['user'],cod_prod]).fetchall()
                    promedio =cur.execute("SELECT AVG (Calificacion) FROM Comentarios WHERE Cod_producto=?",[cod_prod]).fetchone()
                    if row != None:
                        return render_template("MisComentarios.html",Nombre=nombre_prod,path_img=url,Descripcion=descripcion,Precio=precio,Rate=promedio[0],Usuario=session['user'],row=row)
                    else:
                        return render_template("MisComentarios.html",Nombre=nombre_prod,path_img=url,Descripcion=descripcion,Precio=precio,Rate=0,Usuario=session['user'])
                    
            except Error:
                flash("El producto no existe"+Error)
                return redirect('/')

        if request.method=='POST':
            comentario=escape(request.form["mi_comentario"])
            rate=escape(request.form["calificacion"])
            if rate=="":
                flash("Para hacer el comentario, debe darle una calificación al producto.")
                return redirect('/miscomentarios/'+nombre_prod)
            else:
                try:
                    with sqlite3.connect("TJX_productos.db") as con:
                        cur = con.cursor()
                        consulta=cur.execute("SELECT Codigo FROM Productos WHERE Nombre=?",[nombre_prod]).fetchone()
                        cod_prod=consulta[0]
                        cur.execute("INSERT INTO Comentarios (Cod_producto, Usuario, Comentario,Calificacion) VALUES (?,?,?,?)",[cod_prod,session['user'],comentario, rate])
                        con.commit()
                except Error:
                    flash("No se pudo realizar el comentario, inténtelo más tarde")
                    return redirect('/')
        else:
            flash("Para hacer un comentario en el producto. Por favor inicie sesión.")
            return redirect('/login')

        return redirect('/miscomentarios/'+nombre_prod)
    else:
        flash("Para ver sus comentarios y gestionarlos. Por favor inicie sesión")
        return redirect('/login')

@app.route('/editar_comentario/<NombrePd>/<rate>', methods=['GET','POST'])
def editarmiscomentarios(NombrePd,rate):
    if 'user' in session:
        nombre_prod=NombrePd+""
        calif = rate
        if request.method=='GET':
            try:
                with sqlite3.connect("TJX_productos.db") as con:
                    cur = con.cursor()
                    consulta1=cur.execute("SELECT Codigo FROM Productos WHERE Nombre=?",[nombre_prod]).fetchone()
                    cod_prod=consulta1[0]
                    consulta2 = cur.execute("SELECT Id, Comentario FROM Comentarios WHERE Usuario=? AND Cod_producto=? AND Calificacion=?", [session['user'],cod_prod,calif]).fetchone()
                    cod_coment = consulta2[0]
                    comentario = consulta2[1]
                    return render_template("editar_comentario.html",Usuario=session['user'],Comentario=comentario, Nombre=nombre_prod, Rate=calif)
                        
            except Error:
                flash("Algo salió mal, inténtelo más tarde")
                return redirect('/')
            
        if request.method=='POST':
            nuevo_comnt=escape(request.form["coment_nuevo"])
            
            if nuevo_comnt=="":
                flash("Debe escribir algo para modificar el comentario.")
                return redirect('/miscomentarios/'+ nombre_prod)
            else:
                try:
                    with sqlite3.connect("TJX_productos.db") as con:
                        cur = con.cursor()
                        consulta1=cur.execute("SELECT Codigo FROM Productos WHERE Nombre=?",[nombre_prod]).fetchone()
                        cod_prod=consulta1[0]
                        consulta2 = cur.execute("SELECT Id FROM Comentarios WHERE Usuario=? AND Cod_producto=? AND Calificacion=?", [session['user'],cod_prod,calif]).fetchone()
                        cod_coment = consulta2[0]
                        cur.execute("UPDATE Comentarios SET Comentario=? WHERE Id=?",[nuevo_comnt,cod_coment])
                        con.commit()
                        flash("Comentario editado")
                        return redirect('/miscomentarios/'+nombre_prod)
                except Error:
                    flash("Algo salió mal, inténtelo más tarde")
                    return redirect('/')
        
    else:
        flash("Para ver sus comentarios y gestionarlos. Por favor inicie sesión")
        return redirect('/login')
    
@app.route('/miscomentarios/eliminar/<NombrePd>/<rate>', methods = ['GET'])
def eliminarmiscomentarios(NombrePd, rate):
    if 'user' in session:
        nombre_prod=NombrePd+""
        calif = rate
        if request.method=='GET':
            try:
                with sqlite3.connect ("TJX_productos.db") as con:
                    cur = con.cursor()
                    consulta1= cur.execute("SELECT Codigo FROM Productos WHERE Nombre=?",[nombre_prod]).fetchone()
                    cod_prod=consulta1[0]
                    consulta2 = cur.execute("SELECT Id FROM Comentarios WHERE Usuario=? AND Cod_producto=? AND Calificacion=?", [session['user'],cod_prod,calif]).fetchone()
                    cod_coment = consulta2[0]
                    cur.execute("DELETE FROM Comentarios WHERE Id=?",[cod_coment])
                    con.commit()
                    flash("Comentario eliminado")
                    return redirect('/miscomentarios/'+nombre_prod)
            except Error:
                flash("Algo salió mal"+Error)
                return redirect('/miscomentarios/'+nombre_prod)
    return redirect('/miscomentarios/'+nombre_prod)

@app.route('/wishlist', methods=['GET'])
def wishlist():
    if request.method=='GET':
        if 'user' in session:
            try:
                with sqlite3.connect("TJX_productos.db") as con:
                    con.row_factory=sqlite3.Row
                    cur = con.cursor()
                    consult=cur.execute("SELECT Nombre, Descripcion, Precio, URL_prod FROM Wishlist WHERE Usuario=?",[session['user']]).fetchall()
                    if consult != None:
                        return render_template("Wishlist.html", row=consult)
            except Error:
                flash("No se encontraron productos en la lista de deseos")
                return redirect('/perfil')
        else:
            flash("Para ver su Lista de Deseos. Por favor inicie sesión. ")
            return redirect('/login')

    return redirect('/wishlist')

@app.route('/delet_list/<NombrePd>', methods=['POST'])
def elinimarlista(NombrePd):
    if request.method=='POST':
        if 'user' in session:
            try:
                with sqlite3.connect ("TJX_productos.db") as con:
                    cur = con.cursor()
                    nom_pd= NombrePd
                    cur.execute("DELETE FROM Wishlist WHERE Usuario=? AND Nombre=?",[session['user'],nom_pd])
                    con.commit()
                    flash("Producto eliminado")
                    return redirect('/wishlist')
            except Error:
                flash("Algo salió mal"+Error)
                return redirect('/wishlist')
    return redirect('/wishlist')

@app.route('/agregar_producto')
def agregar_producto():
    if 'user' in session:
        try:
            with sqlite3.connect("TJX_productos.db") as con:
                cur = con.cursor()
                query = cur.execute("SELECT Rol FROM Usuarios WHERE Correo = ?",[session['user']]).fetchone()
                rol = query
                if rol[0] == 'Admin':
                    
                    try:
                        with sqlite3.connect("TJX_productos.db") as con:
                                cur = con.cursor()
                                cur.execute('SELECT * FROM Productos')
                                data=cur.fetchall()
                                return render_template('addproduct.html', datosprod = data)
                    except Error:
                        print(Error)
                else:
                    return redirect('/')
        except Error:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/crear_producto')
def editar_producto():
    if 'user' in session:
        try:
            with sqlite3.connect("TJX_productos.db") as con:
                cur = con.cursor()
                query = cur.execute("SELECT Rol FROM Usuarios WHERE Correo = ?",[session['user']]).fetchone()
                rol = query
                if rol[0] == 'Admin':
                    return render_template('save_product.html')
                else:
                    return redirect('/')
        except Error:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    if request.method  == 'POST':
        if 'user' in session:
            try:
                with sqlite3.connect("TJX_productos.db") as con:
                    cur = con.cursor()
                    query = cur.execute("SELECT Rol FROM Usuarios WHERE Correo = ?",[session['user']]).fetchone()
                    rol = query
                    if rol[0] == 'Admin':

                        nombre = escape(request.form["nom_p"])
                        cantidad = escape(request.form["cant_p"])
                        precio = escape(request.form["precio_p"])
                        descripcion = escape(request.form["desc_p"])     
                        
                        if len(nombre)==0 or len(cantidad)==0 or len(precio)==0 or len(descripcion)==0:
                            flash("Algunos campos están vacios")
                            return redirect('/crear_producto')

                        cur.execute("INSERT INTO Productos(Nombre,Descripcion,Precio,Cantidad) VALUES (?,?,?,?)",(nombre,descripcion,precio,cantidad))
                        con.commit()
                        mensaje="Producto agregado con éxito"
                        
                        f = request.files['archivo']
                        filename = secure_filename(f.filename)
                        try:
                            app.config['UPLOAD_FOLDER'] = './static/img/img_products'
                            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
                            cur.execute("UPDATE Productos SET URL_prod=? WHERE Nombre=?",[filename, nombre])
                            con.commit()                     
                        except:
                            mensaje= mensaje+" con imagen por defecto"
                        flash(mensaje) 
                        return redirect("/agregar_producto")                                         
                    else:
                        return redirect('/')
            except Error:
                flash("Registro de producto no completado")
                return redirect('/crear_producto')
        else:
            return redirect('/')

@app.route('/update_product/<string:id>', methods=['POST'])
def actualizar_producto(id):
    if request.method  == 'POST':

        if 'user' in session:
            try:
                with sqlite3.connect("TJX_productos.db") as con:
                    cur = con.cursor()
                    query = cur.execute("SELECT Rol FROM Usuarios WHERE Correo = ?",[session['user']]).fetchone()
                    rol = query
                    if rol[0] == 'Admin':

                        nombre = escape(request.form["nom_p"])
                        cantidad = escape(request.form["cant_p"])
                        precio = escape(request.form["precio_p"])
                        descripcion = escape(request.form["desc_p"]) 

                        cur.execute("UPDATE Productos SET Nombre = ?, Descripcion = ?, Precio= ?, Cantidad = ? WHERE Codigo = ?", [nombre, descripcion, precio, cantidad,id])
                        con.commit()

                        mensaje="Datos actualizados con exito"
                        
                        f = request.files['archivo']
                        filename = secure_filename(f.filename)
                        try:
                            app.config['UPLOAD_FOLDER'] = './static/img/img_products'
                            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
                            cur.execute("UPDATE Productos SET URL_prod=? WHERE Codigo=?",[filename, id])
                            con.commit()                     
                        except:
                            mensaje= mensaje+" sin cambio de imagen"
                        flash(mensaje) 
                        return redirect("/agregar_producto")
                    else:
                        return redirect('/')
            except Error:
                flash("Actualización de producto no completado") 
                return render_template('addproduct.html')
        else:
            return redirect('/')

@app.route('/deletep/<string:id>')
def eliminar_producto(id):
    if 'user' in session:
        try:
            with sqlite3.connect("TJX_productos.db") as con:
                cur = con.cursor()
                query = cur.execute("SELECT Rol FROM Usuarios WHERE Correo = ?",[session['user']]).fetchone()
                rol = query
                if rol[0] == 'Admin':

                    try:
                        with sqlite3.connect("TJX_productos.db") as con:
                            cur = con.cursor()
                            cur.execute('DELETE FROM Productos WHERE Codigo={0}'.format(id))
                            con.commit()
                            flash("Producto borrado Exitosamente")
                            return redirect("/agregar_producto")

                    except Error:
                        flash("No se pudo borrar el producto")
                        return redirect("/agregar_producto")
                else:
                    return redirect('/')
        except Error:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/editp/<string:id>')
def get_producto(id):
    if 'user' in session:
        try:
            with sqlite3.connect("TJX_productos.db") as con:
                cur = con.cursor()
                query = cur.execute("SELECT Rol FROM Usuarios WHERE Correo = ?",[session['user']]).fetchone()
                rol = query
                if rol[0] == 'Admin':

                    try:
                        with sqlite3.connect("TJX_productos.db") as con:
                            cur = con.cursor()
                            cur.execute('SELECT * FROM Productos WHERE Codigo = {0}'.format(id))
                            data=cur.fetchall()
                            return render_template('editproduct.html', datosprod = data[0])
                                            
                    except Error:
                        flash("No se pudo editar el producto")
                        return render_template('editproduct.html')
                else:
                    return redirect('/')
        except Error:
            return redirect('/')
    else:
        return redirect('/')

@app.route('/Tienda', methods=['GET', 'POST'])
def Tienda():
    if request.method == 'GET':
        try:
            with sqlite3.connect('TJX_productos.db') as con:
                        con.row_factory = sqlite3.Row
                        cur = con.cursor()
                        query = cur.execute('SELECT Nombre, Descripcion, URL_prod FROM Productos').fetchall()
                        if query is None:
                            error = 'No hay productos en la tienda, Vuelva mas tarde'
                            flash(error)
                            return render_template('Tienda.html')
                        else:
                            return render_template('Tienda.html', row = query)
        except Error:
            print(Error)
    
    if request.method == 'POST':
        consulta = request.form['consulta'].upper()
        try:
            with sqlite3.connect('TJX_productos.db') as con:
                        con.row_factory = sqlite3.Row
                        cur = con.cursor()
                        query = cur.execute('SELECT Nombre, Descripcion, URL_prod FROM Productos where UPPER(Nombre)= ?', [consulta]).fetchall()
                        
                        if len(query) == 0:
                            error = 'Producto no encontrado, Intente mas tarde'
                            flash(error)
                            return render_template('Tienda.html')
                        else:
                            return render_template('Tienda.html', row = query)
        except Error:
            print(Error)

@app.route('/Eliminar_producto')
def Eliminar_producto():
    return render_template('Eliminar_producto.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000) 