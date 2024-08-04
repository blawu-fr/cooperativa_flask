class Config:
    SECRET_KEY = 'hG&aK!Nl6w0=+5$~'

class DevelopmentConfig(Config):
    DEBUG=True

    # DB configuration
    MYSQL_HOST= 'localhost'
    MYSQL_USER= 'root'
    MYSQL_PASSWORD= 'black593'
    MYSQL_DB= 'coop'
    

    # Flask-Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'enmablackwood@gmail.com'
    MAIL_PASSWORD = 'olnf lbgm oqze heie'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

config={
    'development':DevelopmentConfig
}