from .entities.Prestamo import Prestamo

class ModelPrestamo:
    @classmethod
    def get_by_user_id(cls, db, usuario_id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT prestamo_id, usuario_id, monto, tasa_interes, plazo, fecha_prestamo, fecha_pago_prestamo, tipo_cuenta FROM Prestamos WHERE usuario_id = '{}'".format(usuario_id)
            cursor.execute(sql)
            rows = cursor.fetchall()
            prestamos = []
            for row in rows:
                prestamo = Prestamo(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                prestamos.append(prestamo)
            return prestamos
        except Exception as ex:
            raise Exception(ex)


    @classmethod
    def get_total_prestamos_by_user_id(cls, db, user_id):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT SUM(monto) FROM prestamos WHERE usuario_id = '{}'""".format(user_id)
            cursor.execute(sql)
            row = cursor.fetchone()
            return row[0] if row[0] else 0.0
        except Exception as ex:
            raise Exception(ex)