class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fitness.db'  # Banco local para desenvolvimento
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '2ebfcc42fdd537ac1424f6a28bda320e'