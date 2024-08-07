from functools import wraps
from flask import Flask, render_template, request, url_for, redirect, flash, abort
from flask_mysqldb import MySQL
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf import CSRFProtect
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
from datetime import datetime
from config import config
import logging
import smtplib


# Models:
from models.ModelAhorro import ModelAhorro
from models.ModelAportacion import ModelAportacion
from models.ModelPrestamo import ModelPrestamo
from models.ModelUser import ModelUser
from models.ModelSendEmail import ModelSendEmail

# Entities:
from models.entities.Prestamo import Prestamo
from models.entities.User import User

app = Flask(__name__)

# Configuracion de la aplicacion, importante que se ejecute de primero
app.config.from_object(config['development'])

# CSRF protection
csrf = CSRFProtect()

# Database connection
db = MySQL(app)

# Flask-Login
login_manager_app = LoginManager(app)

# Flask-Mail
mail = Mail(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# Método que retorna el usuario actual de la sesión
@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)

# Método que procura que el usuario tenga permisos de administrador
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

# La ruta default es la del login
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(0, request.form['username'], request.form['password'], None)
        logged_user = ModelUser.login(db, user)
        if logged_user is not None:
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
                flash("Contraseña inválida...")
                return render_template('auth/login.html')
        else:
            flash("Usuario no encontrado...")
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        nombre = request.form.get('nombre', '').strip()
        edad = request.form.get('edad', '').strip()
        direccion = request.form.get('direccion', '').strip()
        telefono = request.form.get('telefono', '').strip()

        # Validaciones
        if not username:
            flash("El nombre de usuario es requerido.")
            return render_template('auth/register.html')

        if not password:
            flash("La contraseña es requerida.")
            return render_template('auth/register.html')

        if not nombre:
            flash("El nombre es requerido.")
            return render_template('auth/register.html')

        if not edad:
            flash("La edad es requerida.")
            return render_template('auth/register.html')

        if not direccion:
            flash("La dirección es requerida.")
            return render_template('auth/register.html')

        if not telefono:
            flash("El teléfono es requerido.")
            return render_template('auth/register.html')

        # Hash de la contraseña
        hashed_password = generate_password_hash(password)

        # Crear usuario
        new_user = User(0, username, hashed_password, 0, nombre)
        success = ModelUser.create_user(db, new_user, edad, direccion, telefono)

        if success:
            flash("Usuario creado satisfactoriamente!")
            return redirect(url_for('login'))
        else:
            flash("Error creando usuario...")
            return render_template('auth/register.html')
    else:
        return render_template('auth/register.html')


# Rutas para admin
@app.route('/admin')
@admin_required
@login_required
def admin():
    users = ModelUser.get_all_users(db)
    for user in users:
        user.prestamos = ModelPrestamo.get_by_user_id(db, user.id)
    return render_template('admin.html', users=users)

@app.route('/admin/create', methods=['POST'])
@admin_required
@login_required
def create_user():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    nombre = request.form.get('nombre', '').strip()
    edad = request.form.get('edad', '').strip()
    direccion = request.form.get('direccion', '').strip()
    telefono = request.form.get('telefono', '').strip()

    # Validaciones
    if not username:
        flash("El nombre de usuario es requerido.")
        return redirect(url_for('admin'))

    if not password:
        flash("La contraseña es requerida.")
        return redirect(url_for('admin'))

    if not nombre:
        flash("El nombre es requerido.")
        return redirect(url_for('admin'))

    if not edad:
        flash("La edad es requerida.")
        return redirect(url_for('admin'))

    if not direccion:
        flash("La dirección es requerida.")
        return redirect(url_for('admin'))

    if not telefono:
        flash("El teléfono es requerido.")
        return redirect(url_for('admin'))

    # Hash de la contraseña
    hashed_password = generate_password_hash(password)

    # Crear usuario
    new_user = User(0, username, hashed_password, 0, nombre)
    success = ModelUser.create_user(db, new_user, edad, direccion, telefono)

    if success:
        flash("Usuario creado satisfactoriamente!")
    else:
        flash("Error creando usuario...")

    return redirect(url_for('admin'))


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

@app.route('/admin/add_prestamo', methods=['POST'])
@admin_required
@login_required
def add_prestamo():
    usuario_id = request.form.get('usuario_id', '').strip()
    monto_str = request.form.get('monto', '').strip()
    tasa_interes_str = request.form.get('tasa_interes', '').strip()
    plazo_str = request.form.get('plazo', '').strip()
    fecha_prestamo = request.form.get('fecha_prestamo', '').strip()
    fecha_pago_prestamo = request.form.get('fecha_pago_prestamo', '').strip()
    tipo_cuenta = request.form.get('tipo_cuenta', '').strip()

    # Validaciones
    if not usuario_id:
        flash("El ID de usuario es requerido.")
        return redirect(url_for('admin'))

    if not monto_str:
        flash("El monto es requerido.")
        return redirect(url_for('admin'))

    if not tasa_interes_str:
        flash("La tasa de interés es requerida.")
        return redirect(url_for('admin'))

    if not plazo_str:
        flash("El plazo es requerido.")
        return redirect(url_for('admin'))

    if not fecha_prestamo:
        flash("La fecha del préstamo es requerida.")
        return redirect(url_for('admin'))

    if not fecha_pago_prestamo:
        flash("La fecha de pago del préstamo es requerida.")
        return redirect(url_for('admin'))

    if not tipo_cuenta:
        flash("El tipo de cuenta es requerido.")
        return redirect(url_for('admin'))

    try:
        monto = float(monto_str)
        tasa_interes = float(tasa_interes_str)
        plazo = int(plazo_str)
    except ValueError:
        flash("El monto, la tasa de interés y el plazo deben ser números válidos.")
        return redirect(url_for('admin'))

    # Crear el préstamo
    new_prestamo = Prestamo(0, usuario_id, monto, tasa_interes, plazo, fecha_prestamo, fecha_pago_prestamo, tipo_cuenta)
    success = ModelPrestamo.insert_prestamo(db, new_prestamo)

    if success:
        flash("Préstamo y cuotas creados satisfactoriamente!")
    else:
        flash("Error creando préstamo y cuotas...")

    return redirect(url_for('admin'))


@app.route('/aportaciones')
@login_required
def aportaciones():
    aportaciones = ModelAportacion.get_by_user_id(db, current_user.id)
    return render_template('aportaciones.html', aportaciones=aportaciones)

@app.route('/ahorros')
@login_required
def ahorros():
    ahorros = ModelAhorro.get_by_user_id(db, current_user.id)
    return render_template('ahorros.html', ahorros=ahorros)

@app.route('/prestamos')
@login_required
def prestamos():
    prestamos = ModelPrestamo.get_by_user_id(db, current_user.id)
    return render_template('prestamos.html', prestamos=prestamos)

@app.route('/finanzas')
@login_required
def finanzas():
    aportaciones = ModelAportacion.get_by_user_id(db, current_user.id)
    ahorros = ModelAhorro.get_by_user_id(db, current_user.id)
    prestamos = ModelPrestamo.get_by_user_id(db, current_user.id)
    total_ahorros = ModelAhorro.get_total_ahorros_by_user_id(db, current_user.id)
    total_aportaciones = ModelAportacion.get_total_aportaciones_by_user_id(db, current_user.id)
    total_prestamos = ModelPrestamo.get_total_prestamos_by_user_id(db, current_user.id)

    # Obtener cuotas y la fecha del siguiente pago para cada préstamo
    cuotas = {}
    fecha_siguiente_pago = {}

    for prestamo in prestamos:
        cuotas[prestamo.id] = ModelPrestamo.get_cuotas_by_prestamo_id(db, prestamo.id)
        fecha_siguiente_pago[prestamo.id] = ModelPrestamo.get_fecha_siguiente_pago(db, prestamo.id)

    return render_template('finanzas.html', aportaciones=aportaciones, ahorros=ahorros, prestamos=prestamos, total_ahorros=total_ahorros, total_prestamos=total_prestamos, total_aportaciones=total_aportaciones, cuotas=cuotas, fecha_siguiente_pago=fecha_siguiente_pago)

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

#cerrar sesion aqui
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/test-email')
def test_email():
    try:
        msg = Message('Test Email',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=['mani-f@hotmail.com'])
        msg.body = 'This is a test email sent from Flask.'
        with mail.record_messages() as outbox:
            mail.send(msg)
            print(outbox)  # Print the sent messages for debugging
        return "Test email sent successfully."
    except smtplib.SMTPException as e:
        app.logger.error(f"SMTP error: {e}")
        return f"SMTP error: {e}"
    except Exception as e:
        app.logger.error(f"Error sending test email: {e}")
        return f"Error sending test email: {e}"


def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Pagina no encontrada</h1>", 404

if __name__ == "__main__":
    csrf.init_app(app)

    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
     

    app.run()

    # Schedule los recordatorios por correo   
    ModelSendEmail.schedule_reminder_emails(app, db, mail)