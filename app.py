import os
from flask import Flask
from flask import render_template, redirect, request, Response, session
from flask_mysqldb import MySQL, MySQLdb
from datetime import datetime
from flask import send_from_directory


app = Flask(__name__,template_folder='Template')

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='biblioteca'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/img/<imagen>')
def img(imagen):
    print(imagen)
    return send_from_directory(os.path.join('Template/img'), imagen)

@app.route("/css/<archivocss>")
def css(archivocss):
    return send_from_directory(os.path.join('Template/css'), archivocss)

@app.route('/libros')
def libros():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM libros")
    libros = cur.fetchall()
    cur.close()

    return render_template('libros.html', libros=libros)

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/subir')
def subir():

    if not 'logueado' in session:
        return redirect('/')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM libros")
    libros = cur.fetchall()
    cur.close()
    print(libros)
    return render_template('subir.html', libros=libros)

@app.route('/subir/guardar', methods=['POST'])
def libros_guardar():
    _nombre = request.form['txtNombre']
    _url = request.form['txtURL']
    _archivo = request.files['txtImagen']

    print(_nombre)
    print(_url)
    print(_archivo)

    tiempo= datetime.now()
    horaActual=tiempo.strftime('%Y%H%M%S')

    nuevoNombre=""
    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        _archivo.save("Template/img/"+nuevoNombre)

    cur = mysql.connection.cursor()
    cur.execute(" INSERT INTO libros (nombre, url, imagen) VALUES (%s, %s, %s)", (_nombre, _url, nuevoNombre))
    mysql.connection.commit()

    return redirect('/libros')

@app.route('/libros/borrar', methods=['POST'])
def borrar():
    _id = request.form['txtID']
    _id = int(_id)

    cur = mysql.connection.cursor()
    cur.execute('SELECT imagen FROM libros WHERE id = %s', (_id,))
    libro = cur.fetchone()
    cur.close()

    if libro and 'imagen' in libro:
        imagen_path = os.path.join("Template", "img", libro['imagen'])

        if os.path.exists(imagen_path):
            os.unlink(imagen_path)

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM libros WHERE id = %s", (_id,))
    mysql.connection.commit()
    cur.close()
    return redirect('/subir')

@app.route('/cerrar')
def login_cerrar():
    session.clear()
    return redirect('/')

#Funcion de Login

@app.route('/acceso-login', methods= ["GET", "POST"])
def login():

    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword':
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']

        cur=mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE correo = %s AND password = %s', (_correo, _password))
        account = cur.fetchone()

        if account:
            session['logueado'] = True
            session['id'] = account['id']

            return render_template("admin.html")
        else:

            return render_template('login.html', mensaje="Usuario o clave incorrecta")


#Funcion de Registro

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/crear-registro', methods= ["GET", "POST"])
def crear_registro():

    correo=request.form['txtCorreo']
    password = request.form['txtPassword']
    nombre = request.form['txtNombre']


    cur = mysql.connection.cursor()
    cur.execute(" INSERT INTO usuarios (nombre, correo, password) VALUES (%s, %s, %s)", (nombre, correo, password))
    mysql.connection.commit()

    return render_template("login.html", mensaje2="Usuario registrado exitosamente!")

if __name__ == '__main__':
    app.secret_key="Luis2863"
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)