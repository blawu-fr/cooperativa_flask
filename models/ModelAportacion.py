from .entities.Aportacion import Aportacion

class ModelAportacion:
    @classmethod
    def get_by_user_id(cls, db, usuario_id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT aportacion_id, usuario_id, monto, fecha_aportacion FROM Aportaciones WHERE usuario_id = '{}'".format(usuario_id)
            cursor.execute(sql)
            rows = cursor.fetchall()
            aportaciones = []
            for row in rows:
                aportacion = Aportacion(row[0], row[1], row[2], row[3])
                aportaciones.append(aportacion)
            return aportaciones
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def get_total_aportaciones_by_user_id(cls, db, user_id):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT SUM(monto) FROM aportaciones WHERE usuario_id = '{}'""".format(user_id)
            cursor.execute(sql)
            row = cursor.fetchone()
            return row[0] if row[0] else 0.0
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def insert_aportacion(cls, db, usuario_id, monto):
        try:
            cursor = db.connection.cursor()
            sql = """INSERT INTO Aportaciones (usuario_id, monto) VALUES (%s, %s)"""
            values = (usuario_id, monto)
            cursor.execute(sql, values)
            db.connection.commit()
        except Exception as ex:
            raise Exception(ex)
