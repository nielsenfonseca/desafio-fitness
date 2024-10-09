from flask import request, jsonify, session
from backend.models import db, User, Workout, Group
from datetime import datetime, timedelta
from collections import defaultdict
import calendar
import cloudinary
import cloudinary.uploader

# Configuração do Cloudinary
cloudinary.config(
  cloud_name='dkwaxm3es',
  api_key='999638577897831',
  api_secret='CyekgXfTQZQ8bm5ZNnyS7c7w2IY'
)

# Função para configurar as rotas
def configure_routes(app):

    # 1. Registro de um novo usuário com senha
    # Rota de registro de usuário
    @app.route('/register_user', methods=['POST'])
    def register_user():
        data = request.get_json()
        name = data.get('name')
        username = data.get('username')
        password = data.get('password')

        if not name or not username or not password:
            return jsonify({'error': 'Nome, nome de usuário e senha são obrigatórios'}), 400

        # Verifica se o nome de usuário já existe
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Nome de usuário já existe'}), 400

        # Se for o primeiro usuário, ele será o admin
        is_admin = False
        if User.query.count() == 0:
            is_admin = True  # Define o primeiro usuário como admin

        # Cria o usuário
        new_user = User(name=name, username=username, is_admin=is_admin)
        new_user.set_password(password)  # Define a senha (hash)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Usuário criado com sucesso!'}), 201
    
    # 2. Login do usuário
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Verifica se o usuário existe e a senha está correta
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return jsonify({
                'message': 'Login bem-sucedido', 
                'username': username, 
                'name': user.name,
                'is_admin': user.is_admin
            }), 200
        else:
            return jsonify({'error': 'Credenciais inválidas'}), 401

    # 3. Logout do usuário
    @app.route('/logout', methods=['POST'])
    def logout():
        session.pop('user_id', None)
        return jsonify({'message': 'Logout bem-sucedido'}), 200

    # 4. Registrar um treino
    # Função para registrar um treino com upload de foto
    @app.route('/register_workout', methods=['POST'])
    def register_workout():
        data = request.form
        user_id = data.get('user_id')
        duration = data.get('duration')
        exercise_type = data.get('exercise_type')
        effort_level = data.get('effort_level')

        # Verifica se há um arquivo de foto anexado
        file = request.files.get('file')

        # Pega o nome de usuário com base no user_id
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        if file:
            # Faz o upload da imagem para o Cloudinary e adiciona o nome do usuário como tag
            upload_result = cloudinary.uploader.upload(file, tags=[user.username])
            # URL pública da imagem
            file_url = upload_result.get('secure_url')
        else:
            file_url = None

        # Cria o treino e salva no banco de dados
        workout = Workout(
            user_id=user_id,
            duration=duration,
            exercise_type=exercise_type,
            effort_level=effort_level,
            date=datetime.now(),
            photo_url=file_url
        )
        db.session.add(workout)
        db.session.commit()

        return jsonify({'message': 'Treino registrado com sucesso!'}), 201

    # 5. Exibir o desempenho de um usuário
    @app.route('/user_performance/<int:user_id>', methods=['GET'])
    def user_performance(user_id):
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Busca todos os treinos do usuário
        workouts = Workout.query.filter_by(user_id=user.id).all()
        total_workouts = len(workouts)

        # Retorna o desempenho
        return jsonify({
            'name': user.name,
            'total_workouts': total_workouts,
            'fines': user.fines
        })

    # 6. Função para calcular multas de forma dinâmica ao consultar, agrupando por mês
    # Função para calcular multas de forma dinâmica ao consultar, agrupando por mês
    @app.route('/user_fines_dynamic/<string:username>', methods=['GET'])
    def user_fines_dynamic(username):
        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Busca todos os treinos do usuário
        workouts = Workout.query.filter_by(user_id=user.id).all()

        # Dicionário para armazenar o número de treinos por semana
        weekly_workouts = {}

        # Agrupa os treinos por semana e soma o total de treinos na semana
        for workout in workouts:
            # Obtém a data de início da semana (segunda-feira)
            week_start = (workout.date - timedelta(days=workout.date.weekday())).date()

            # Se a semana já existe no dicionário, somamos, senão criamos uma nova entrada
            if week_start in weekly_workouts:
                weekly_workouts[week_start] += 1
            else:
                weekly_workouts[week_start] = 1

        # Variável para armazenar o total de multas
        total_fines = 0
        fines_detail = defaultdict(list)

        # Para cada semana, calcular a multa e consolidar corretamente
        for week_start, count in weekly_workouts.items():
            week_end = week_start + timedelta(days=6)  # Calcula o domingo da mesma semana
            month_year = week_start.strftime('%Y-%m')  # Identifica o mês e ano

            if count < 3:
                fine_for_week = (3 - count) * 5  # R$ 5,00 por treino faltante
                total_fines += fine_for_week
            else:
                fine_for_week = 0  # Sem multa se atingiu a meta

            # Adiciona os detalhes da semana no mês correto (consolidado)
            fines_detail[month_year].append({
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': week_end.strftime('%Y-%m-%d'),
                'workouts': count,  # Exibe o total consolidado de treinos na semana
                'fine': fine_for_week
            })

        # Organiza os dados por mês para o frontend
        formatted_fines_detail = []
        for month_year, weeks in fines_detail.items():
            month_name = calendar.month_name[int(month_year.split('-')[1])]  # Nome do mês
            formatted_fines_detail.append({
                'month': f"{month_name} {month_year.split('-')[0]}",  # Exibe o mês e ano
                'weeks': weeks
            })

        return jsonify({
            'name': user.name,
            'total_fines': total_fines,
            'fines_detail': formatted_fines_detail
        })

    # 7. Criar grupos
    @app.route('/create_group', methods=['POST'])
    def create_group():
        data = request.get_json()
        group_name = data.get('name')

        if not group_name:
            return jsonify({'error': 'Nome do grupo é obrigatório'}), 400

        # Verifica se o nome do grupo já existe
        if Group.query.filter_by(name=group_name).first():
            return jsonify({'error': 'Grupo já existe com este nome'}), 400

        # Cria o grupo
        new_group = Group(name=group_name)
        db.session.add(new_group)
        db.session.commit()

        return jsonify({'message': 'Grupo criado com sucesso!'}), 201

    #8. Deletar grupos
    @app.route('/delete_group', methods=['POST'])
    def delete_group():
        data = request.get_json()
        group_id = data.get('group_id')

        group = Group.query.get(group_id)

        if not group:
            return jsonify({'error': 'Grupo não encontrado'}), 404

        # Remove todos os membros do grupo antes de deletar
        for user in group.members:
            user.group_id = None  # Desassocia os usuários do grupo

        db.session.delete(group)
        db.session.commit()

        return jsonify({'message': 'Grupo deletado com sucesso!'}), 200
    
    #9. Atribuir grupo pra user
    @app.route('/assign_user_to_group', methods=['POST'])
    def assign_user_to_group():
        data = request.get_json()
        username = data.get('username')  # Obter o username ao invés do user_id
        group_id = data.get('group_id')

        # Verificar se o grupo existe
        group = Group.query.get(group_id)
        if not group:
            return jsonify({'error': 'Grupo não encontrado'}), 404

        # Buscar o usuário pelo username
        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Atribuir o grupo ao usuário
        user.group_id = group_id
        db.session.commit()

        return jsonify({'message': f'{user.name} foi adicionado ao grupo {group.name}'}), 200

    #9. pegar nome do user pelo id
    @app.route('/get_user_id/<username>', methods=['GET'])
    def get_user_id(username):
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({"user_id": user.id}), 200
        else:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
    #9. pegar nomes dos usuários
    # Pegar nomes de usuários e seus nomes completos
    @app.route('/get_usernames', methods=['GET'])
    def get_usernames():
        users = User.query.all()
        user_data = [{'username': user.username, 'name': user.name} for user in users]
        return jsonify({'users': user_data})
        
    #10. performance pelo nome de usuário
    @app.route('/user_performance_by_username/<string:username>', methods=['GET'])
    def user_performance_by_username(username):
        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Busca todos os treinos do usuário
        total_workouts = len(user.workouts)

        # Retorna o desempenho geral
        return jsonify({
            'name': user.name,
            'total_workouts': total_workouts,  # Total de treinos desde o início
            'fines': user.fines,  # Multa total acumulada
            'group': user.group.name if user.group else None  # Grupo, se houver
        })
        
    # 11. Pegar nome do grupo pelo ID e seus membros
    @app.route('/get_groups', methods=['GET'])
    def get_groups():
        groups = Group.query.all()
        group_list = []
        
        for group in groups:
            members = [user.name for user in group.members]  # Obter os nomes reais dos membros do grupo
            group_list.append({
                'id': group.id,
                'name': group.name,
                'members': members  # Inclui os nomes dos membros no retorno
            })
            
        return jsonify({'groups': group_list})

    # 12. Pegar usuários sem grupo
    @app.route('/get_users_without_group', methods=['GET'])
    def get_users_without_group():
        users_without_group = User.query.filter_by(group_id=None).all()
        usernames = [user.username for user in users_without_group]
        return jsonify({'usernames': usernames})