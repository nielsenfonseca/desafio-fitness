from flask import Flask, session
from backend.routes import configure_routes
from backend.database import init_db
from backend.models import db
from flask_migrate import Migrate
from config import get_config  # Importa a função que define o ambiente
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configurações da aplicação com base no ambiente (desenvolvimento ou produção)
app.config.from_object(get_config())

# Necessário para as sessões
app.config['SECRET_KEY'] = app.config.get('SECRET_KEY', '2ebfcc42fdd537ac1424f6a28bda320e')  # Usa a chave do config ou o valor padrão

# Inicializa o banco de dados e as rotas
init_db(app)
configure_routes(app)

# Inicializa as migrações
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)
