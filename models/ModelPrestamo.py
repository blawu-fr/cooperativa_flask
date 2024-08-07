from models.ModelAhorro import ModelAhorro
from models.ModelAportacion import ModelAportacion
from .entities.Prestamo import Prestamo
from datetime import datetime, timedelta

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
        

    @classmethod
    def insert_prestamo(cls, db, prestamo):
        try:
            cursor = db.connection.cursor()
            sql = """INSERT INTO prestamos (usuario_id, monto, tasa_interes, plazo, fecha_prestamo, fecha_pago_prestamo, tipo_cuenta) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            values = (prestamo.usuario_id, prestamo.monto, prestamo.tasa_interes, prestamo.plazo, prestamo.fecha_prestamo, prestamo.fecha_pago_prestamo, prestamo.tipo_cuenta)
            cursor.execute(sql, values)
            db.connection.commit()

            prestamo_id = cursor.lastrowid
            cls.insert_prestamo_cuotas(db, prestamo_id, prestamo.monto, prestamo.plazo, prestamo.fecha_pago_prestamo,prestamo.tasa_interes)
            
            # Insertar un nuevo registro de ahorro con el monto del préstamo
            if prestamo.tipo_cuenta == 'Ahorros':
                ModelAhorro.insert_ahorro(db, prestamo.usuario_id, prestamo.monto)
            elif prestamo.tipo_cuenta == 'Aportaciones':
                ModelAportacion.insert_aportacion(db, prestamo.usuario_id, prestamo.monto)

            return True
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def insert_prestamo_cuotas(cls, db, prestamo_id, monto, plazo, fecha_inicio_pago, tasa_interes):
        try:
            cursor = db.connection.cursor()
            monto_cuota = (monto * tasa_interes * plazo) / plazo
            fecha_pago = datetime.strptime(fecha_inicio_pago, "%Y-%m-%d")

            for cuota in range(1, plazo + 1):
                sql = """INSERT INTO prestamos_cuotas (prestamo_id, numero_cuota, fecha_pago, monto_cuota) 
                         VALUES (%s, %s, %s, %s)"""
                values = (prestamo_id, cuota, fecha_pago.strftime("%Y-%m-%d"), monto_cuota) #agregar interes
                cursor.execute(sql, values)
                fecha_pago += timedelta(days=31)  # Incrementar la fecha de pago en un mes

            db.connection.commit()
        except Exception as ex:
            raise Exception(ex)
    
    @classmethod
    def get_cuotas_by_prestamo_id(cls, db, prestamo_id):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT numero_cuota, fecha_pago, monto_cuota FROM prestamos_cuotas WHERE prestamo_id = %s"""
            cursor.execute(sql, (prestamo_id,))
            rows = cursor.fetchall()
            cuotas = [{'numero_cuota': row[0], 'fecha_pago': row[1], 'monto_cuota': row[2]} for row in rows]
            return cuotas
        except Exception as ex:
            raise Exception(ex)
    
    @classmethod
    def get_fecha_siguiente_pago(cls, db, prestamo_id):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT fecha_pago FROM prestamos_cuotas WHERE prestamo_id = %s ORDER BY fecha_pago ASC LIMIT 1"""
            cursor.execute(sql, (prestamo_id,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as ex:
            raise Exception(ex)