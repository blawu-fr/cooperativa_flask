from .entities.User import User


class ModelUser():
    
    @classmethod
    def login(self,db,user):
        try:
            cursor=db.connection.cursor()
            sql="""select usuario_id,email,contrasena,id_rol,nombre from usuarios 
                    where email = '{}'""".format(user.username)
            cursor.execute(sql)
            row=cursor.fetchone()
            if row != None:
                user=User(row[0],row[1],User.check_password(row[2],user.password),row[3],row[4])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def get_by_id(self,db,id):
        try:
            cursor=db.connection.cursor()
            sql="""select usuario_id,email,id_rol,nombre from usuarios 
                    where usuario_id = '{}'""".format(id)
            cursor.execute(sql)
            row=cursor.fetchone()
            if row != None:
               return User(row[0],row[1],None,row[2],row[3])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def create_user(self, db, user, edad, direccion, telefono):
        try:
            cursor = db.connection.cursor()
            sql = """INSERT INTO usuarios (email, contrasena, nombre, edad, direccion, telefono) 
                     VALUES ('{}', '{}', '{}', {}, '{}', '{}')""".format(
                        user.username, user.password, user.nombre, edad, direccion, telefono)
            cursor.execute(sql)
            db.connection.commit()
            return True
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def get_all_users(cls, db):
        try:
            cursor = db.connection.cursor()
            sql = """SELECT usuario_id, email, nombre, edad, direccion, telefono FROM usuarios"""
            cursor.execute(sql)
            rows = cursor.fetchall()
            users = []
            for row in rows:
                user = User(row[0], row[1], None, None, row[2])
                user.edad = row[3]
                user.direccion = row[4]
                user.telefono = row[5]
                users.append(user)
            return users
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def update_user(cls, db, id, username, nombre, edad, direccion, telefono):
        try:
            cursor = db.connection.cursor()
            sql = """UPDATE usuarios SET email = '{}', nombre = '{}', edad = {}, direccion = '{}', telefono = '{}' 
                     WHERE usuario_id = '{}'""".format(username, nombre, edad, direccion, telefono, id)
            cursor.execute(sql)
            db.connection.commit()
            return True
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def delete_user(cls, db, id):
        try:
            cursor = db.connection.cursor()
            sql = """DELETE FROM usuarios WHERE usuario_id = '{}'""".format(id)
            cursor.execute(sql)
            db.connection.commit()
            return True
        except Exception as ex:
            raise Exception(ex)