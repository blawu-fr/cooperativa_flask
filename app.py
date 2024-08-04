from functools import wraps
from flask import Flask, render_template, request, url_for,redirect,flash,abort 
from flask_mysqldb import MySQL
from flask_login import LoginManager, current_user,login_user,logout_user,login_required
from flask_wtf import CSRFProtect
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
from datetime import datetime
from config import config




#Models:
from models.ModelAhorro import ModelAhorro
from models.ModelAportacion import ModelAportacion
from models.ModelPrestamo import ModelPrestamo
from models.ModelUser import ModelUser
from models.ModelSendEmail import ModelSendEmail

#Entities:
from models.entities.User import User



app = Flask(__name__)


# CSRF protection
csrf = CSRFProtect()

# Database conn
db = MySQL(app)

# Flask-Login
login_manager_app = LoginManager(app)

# Flask-Mail
mail = Mail(app)

#Metodo que retorna el usuario actual de la sesion
@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db,id)

#Metodo que procura que el usuario tenga permisos de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión para acceder a esta página.")
            return redirect(url_for('login'))
        if current_user.id_rol != 1:
            flash("No tienes permisos de administrador para acceder a esta página.")
            return redirect(url_for('finanzas'))
        return f(*args, **kwargs)
    return decorated_function



#La ruta default es la del login
@app.route('/')
def index():
    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user= User(0,request.form['username'],request.form['password'],None)
        logged_user=ModelUser.login(db,user)
        if logged_user != None:
            if logged_user.password:
                login_user(logged_user)
                if logged_user.id_rol == 1:
                # Esta condicional es opcional, es simplemente para que cuando un 
                # administrador entre se le redirije directamente a la vista de admin, 
                # de manera que no tenga que introducir la ruta manualmente
                # lo aclaro porque a simple vista, parece algo redundante 
                    return redirect(url_for('admin'))
                else:
                    return redirect(url_for('finanzas'))
            else:
                flash("Contraseña invalida...")
                return render_template('auth/login.html')
        else:
            flash("usuario no encontrado...")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')
    

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        nombre = request.form['nombre']
        edad = request.form['edad']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        hashed_password = generate_password_hash(password)
        new_user = User(0, username, hashed_password, 0, nombre)
        #otra variable porque edad, direccion y telefono no son atributos de la entidad usuario
        success = ModelUser.create_user(db, new_user, edad, direccion, telefono)
        if success:
            flash("Usuario creado satisfactoriamente!")
            return redirect(url_for('login'))
        else:
            flash("Error creando usuario...")
            return render_template('auth/register.html')
    else:
        return render_template('auth/register.html')


#rutas para admin
@app.route('/admin')
@admin_required
@login_required
def admin():
    users = ModelUser.get_all_users(db)
    return render_template('admin.html', users=users)

#rutas para admin
@app.route('/admin/create', methods=['POST'])
@admin_required
@login_required
def create_user():
    username = request.form['username']
    password = request.form['password']
    nombre = request.form['nombre']
    edad = request.form['edad']
    direccion = request.form['direccion']
    telefono = request.form['telefono']
    hashed_password = generate_password_hash(password)
    new_user = User(0, username, hashed_password, 0, nombre)
    #otra variable porque edad, direccion y telefono no son atributos de la entidad usuario
    success = ModelUser.create_user(db, new_user, edad, direccion, telefono)
    if success:
        flash("Usuario creado satisfactoriamente!")
    else:
        flash("Error creando usuario...")
    return redirect(url_for('admin'))

#rutas para admin
@app.route('/admin/edit/<int:id>', methods=['POST'])
@admin_required
@login_required
def edit_user(id):
    username = request.form['username']
    nombre = request.form['nombre']
    edad = request.form['edad']
    direccion = request.form['direccion']
    telefono = request.form['telefono']
    success = ModelUser.update_user(db, id, username, nombre, edad, direccion, telefono)
    if success:
        flash("Usuario actualizado satisfactoriamente!")
    else:
        flash("Error actualizando usuario...")
    return redirect(url_for('admin'))

#rutas para admin
@app.route('/admin/delete/<int:id>')
@admin_required
@login_required
def delete_user(id):
    success = ModelUser.delete_user(db, id)
    if success:
        flash("Usuario eliminado satisfactoriamente!")
    else:
        flash("Error eliminando usuario...")
    return redirect(url_for('admin'))


#No es usada, puede llegar a ser necesaria o incluida en el futuro
@app.route('/aportaciones')
@login_required
def aportaciones():
    aportaciones = ModelAportacion.get_by_user_id(db, current_user.id)
    return render_template('aportaciones.html', aportaciones=aportaciones)

#No es usada, puede llegar a ser necesaria o incluida en el futuro
@app.route('/ahorros')
@login_required
def ahorros():
    ahorros = ModelAhorro.get_by_user_id(db, current_user.id)
    return render_template('ahorros.html', ahorros=ahorros)

#No es usada, puede llegar a ser necesaria o incluida en el futuro
@app.route('/prestamos')
@login_required
def prestamos():
    prestamos = ModelPrestamo.get_by_user_id(db, current_user.id)
    return render_template('prestamos.html', prestamos=prestamos)

#Incluye las 3 vistas anteriores, las cuales fueron reemplazadas por esta
@app.route('/finanzas')
@login_required
def finanzas():
    aportaciones = ModelAportacion.get_by_user_id(db, current_user.id)
    ahorros = ModelAhorro.get_by_user_id(db, current_user.id)
    prestamos = ModelPrestamo.get_by_user_id(db, current_user.id)
    total_ahorros = ModelAhorro.get_total_ahorros_by_user_id(db, current_user.id)
    total_aportaciones = ModelAportacion.get_total_aportaciones_by_user_id(db, current_user.id)
    total_prestamos = ModelPrestamo.get_total_prestamos_by_user_id(db, current_user.id)
    return render_template('finanzas.html', aportaciones=aportaciones, ahorros=ahorros, prestamos=prestamos, total_ahorros=total_ahorros,total_prestamos=total_prestamos,total_aportaciones=total_aportaciones)

#No es usada, puede llegar a ser necesaria o incluida en el futuro
@app.route('/home')
@login_required
def home():
    return render_template('home.html')


#cerrar sesion aqui
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#manejo de errores
def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Pagina no encontrada</h1>", 404


if __name__ == "__main__":
    app.config.from_object(config['development'])
    csrf.init_app(app) #OJO: El secret key debe de estar asignado para este punto, si no, eplota

    #manejo de errores
    app.register_error_handler(401,status_401)
    app.register_error_handler(404,status_404)

    #  # Test envio de correos
    # ModelSendEmail.send_reminder_emails(app, db, mail)

    
      # Schedule los recordatorios por correo   
    ModelSendEmail.schedule_reminder_emails(app, db, mail)

    
    app.run()

