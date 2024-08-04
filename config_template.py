class Config:
    SECRET_KEY = 'ur secret key'

class DevelopmentConfig(Config):
    DEBUG=True

    # DB configuration
    MYSQL_HOST= ''
    MYSQL_USER= ''
    MYSQL_PASSWORD= ''
    MYSQL_DB= ''
    

    # Flask-Mail configuration
    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'example@mail.com'
    MAIL_PASSWORD = 'ur_psswrd'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

# config={
#     'development':DevelopmentConfig
# }