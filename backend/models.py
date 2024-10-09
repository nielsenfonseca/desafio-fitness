from datetime import datetime
from .database import db
from werkzeug.security import generate_password_hash, check_password_hash

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Relacionamento com os usuários (membros do grupo)
    members = db.relationship('User', back_populates='group')

    def __repr__(self):
        return f'<Group {self.name}>'

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)  # Nome de usuário único
    password_hash = db.Column(db.String(128), nullable=False)  # Armazenamos o hash da senha
    total_workouts = db.Column(db.Integer, default=0)
    fines = db.Column(db.Float, default=0.0)
    
    # Nova coluna para identificar se o usuário é administrador
    is_admin = db.Column(db.Boolean, default=False)

    # Nova coluna para armazenar a última semana em que as multas foram calculadas
    last_fine_week = db.Column(db.Date, nullable=True)  # Data da última verificação de multas

    # Chave estrangeira para a tabela de grupos
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))  # Conecta o usuário ao grupo
    
    # Relacionamento com o grupo
    group = db.relationship('Group', back_populates='members')
    
    # Relacionamento com os treinos
    workouts = db.relationship('Workout', backref='user', lazy=True)

    # Métodos para configurar e verificar a senha
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name}>'

class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duração do treino em minutos
    exercise_type = db.Column(db.String(50), nullable=False)  # Tipo de exercício (Corrida, Caminhada, etc.)
    effort_level = db.Column(db.Integer, nullable=False)  # Nível de esforço do treino (1 a 10)
    
    # Novo campo para armazenar a URL da foto do treino
    photo_url = db.Column(db.String(255), nullable=True)  # URL da foto enviada, se houver

    def __repr__(self):
        return f'<Workout User ID: {self.user_id}, Duration: {self.duration} minutes, Type: {self.exercise_type}, Effort: {self.effort_level}, Photo URL: {self.photo_url}>'