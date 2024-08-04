from flask_mail import Message
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

class ModelSendEmail:
    
    @classmethod
    def send_reminder_emails(cls, app, db, mail):
        try:
            with app.app_context():
                cursor = db.connection.cursor()
                sql = """SELECT p.prestamo_id, p.usuario_id, p.monto, p.fecha_pago_prestamo, u.email, u.nombre
                         FROM prestamos p
                         JOIN usuarios u ON p.usuario_id = u.usuario_id
                         WHERE DATE(p.fecha_pago_prestamo) = DATE_ADD(CURDATE(), INTERVAL 1 DAY)"""
                cursor.execute(sql)
                rows = cursor.fetchall()
                for row in rows:
                    prestamo_id, usuario_id, monto, fecha_pago_prestamo, email, nombre = row
                    msg = Message('Recordatorio de Pago de Préstamo',
                                  sender=app.config['MAIL_USERNAME'],
                                  recipients=[email])
                    msg.body = f"Hola {nombre},\n\nEste es un recordatorio de que tu pago de préstamo de ${monto} vence mañana ({fecha_pago_prestamo}).\n\nGracias."
                    mail.send(msg)
        except Exception as e:
            print(f"Error: {e}")

    @classmethod
    def schedule_reminder_emails(cls, app, db, mail):
        scheduler = BackgroundScheduler()
        scheduler.add_job(func=lambda: cls.send_reminder_emails(app, db, mail), trigger="interval", days=1)
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
