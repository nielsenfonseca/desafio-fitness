import os

class Config:
    SECRET_KEY = '2ebfcc42fdd537ac1424f6a28bda320e'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    # Banco de dados local para desenvolvimento
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fitness.db'

class ProductionConfig(Config):
    # Banco de dados Postgres no Supabase para produção
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres.tpavwcyenfhucopzthrm:StihelS2009000@aws-0-sa-east-1.pooler.supabase.com:6543/postgres'

# Função que seleciona a configuração com base na variável de ambiente
def get_config():
    env = os.getenv('FLASK_ENV', 'development')  # 'development' é o padrão
    if env == 'production':
        return ProductionConfig
    return DevelopmentConfig