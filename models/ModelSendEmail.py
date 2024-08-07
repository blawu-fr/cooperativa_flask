from flask_mail import Message
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

class ModelSendEmail:
    
    @classmethod
    def send_reminder_emails(cls, app, db, mail):
        try:
            with app.app_context():
                cursor = db.connection.cursor()
                sql = """SELECT c.prestamo_id, p.usuario_id, c.monto_cuota, c.fecha_pago, u.email, u.nombre
                         FROM prestamos_cuotas c
                         JOIN prestamos p ON c.prestamo_id = p.prestamo_id
                         JOIN usuarios u ON p.usuario_id = u.usuario_id
                         WHERE DATE(c.fecha_pago) = DATE_ADD(CURDATE(), INTERVAL 1 DAY)"""
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    prestamo_id, usuario_id, monto_cuota, fecha_pago, email, nombre = row
                    msg = Message('Recordatorio de Pago de Cuota de Préstamo',
                                  sender=app.config['MAIL_USERNAME'],
                                  recipients=[email])
                    msg.body = (f"Hola {nombre},\n\nEste es un recordatorio de que tu cuota de préstamo de ${monto_cuota} "
                                f"vence mañana ({fecha_pago}).\n\nGracias.")
                    mail.send(msg)
        except Exception as e:
            print(f"Error: {e}")

            
    #esto agenda los correos, es la que se llamara en la app
    #correra en "segundo plano"
    @classmethod
    def schedule_reminder_emails(cls, app, db, mail):
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=lambda: cls.send_reminder_emails(app, db, mail), trigger="interval", days=1)# seteado para que avise un dia antes
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
