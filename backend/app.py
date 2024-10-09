from flask import Flask, session
from backend.routes import configure_routes
from backend.database import init_db
from backend.models import db

app = Flask(__name__)

# Configurações da aplicação
app.config.from_object('config')

# Necessário para as sessões
app.config['SECRET_KEY'] = '2ebfcc42fdd537ac1424f6a28bda320e'  # Uma chave segura

# Inicializa o banco de dados e as rotas
init_db(app)
configure_routes(app)

# Cria todas as tabelas
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)