from flask import Flask, session
from backend.routes import configure_routes
from backend.database import init_db
from backend.models import db
from config import get_config  # Importa a função que define o ambiente

app = Flask(__name__)

# Configurações da aplicação com base no ambiente (desenvolvimento ou produção)
app.config.from_object(get_config())

# Necessário para as sessões
app.config['SECRET_KEY'] = app.config.get('SECRET_KEY', '2ebfcc42fdd537ac1424f6a28bda320e')  # Usa a chave do config ou o valor padrão

# Inicializa o banco de dados e as rotas
init_db(app)
configure_routes(app)

# Cria todas as tabelas (caso ainda não existam)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
