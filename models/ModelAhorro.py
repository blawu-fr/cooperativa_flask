from .entities.Ahorro import Ahorro
from datetime import datetime

class ModelAhorro:
    @classmethod
    def get_by_user_id(cls, db, usuario_id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT ahorro_id, usuario_id, monto, fecha_ahorro FROM Ahorros WHERE usuario_id = '{}'".format(usuario_id)
            cursor.execute(sql)
            rows = cursor.fetchall()
            ahorros = []
            for row in rows:
                ahorro = Ahorro(row[0], row[1], row[2], row[3])
                ahorros.append(ahorro)
            return ahorros
        except Exception as ex:
            raise Exception(ex)



    @classmethod
    def get_total_ahorros_by_user_id(cls, db, user_id):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT SUM(monto) FROM ahorros WHERE usuario_id = '{}'""".format(user_id)
            cursor.execute(sql)
            row = cursor.fetchone()
            return row[0] if row[0] else 0.0
        except Exception as ex:
            raise Exception(ex) 
        

    @classmethod
    def insert_ahorro(cls, db, usuario_id, monto):
        try:
            cursor = db.connection.cursor()
            sql = """INSERT INTO Ahorros (usuario_id, monto) VALUES (%s, %s)"""
            values = (usuario_id, monto)
            cursor.execute(sql, values)
            db.connection.commit()
        except Exception as ex:
            raise Exception(ex)