import streamlit as st
import requests
import os    

# Definir o caminho base do diretório atual
base_path = os.path.dirname(__file__)

# Construir o caminho completo da imagem
logo_path = os.path.join(base_path, "utils", "logo.png")

API_BASE_URL = "http://127.0.0.1:5000"

# Custom CSS to style the sidebar (navbar)
sidebar_style = """
    <style>
        /* Change the background color of the sidebar */
        [data-testid="stSidebar"] {
            background-color: #995e98;
        }
        
        /* Change the font color in the sidebar */
        [data-testid="stSidebar"] .css-1d391kg {
            color: white;
        }
        
        /* Center the logo and set its size */
        [data-testid="stSidebar"] .css-1y4p8pa {
            display: flex;
            justify-content: center;
        }

        /* Custom style for the image */
        img {
            max-width: 70%;  /* Você pode ajustar a porcentagem para alterar o tamanho */
            height: auto;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }

        button[title="View fullscreen"]{
            visibility: hidden;
        }
    </style>
"""

# Inject the CSS into the Streamlit app
st.markdown(sidebar_style, unsafe_allow_html=True)

# Função de Cadastro
def register():
    st.title("Cadastrar Novo Usuário")

    # Inputs do formulário de cadastro
    name = st.text_input("Nome Completo")
    username = st.text_input("Nome de Usuário")
    password = st.text_input("Senha", type="password")
    confirm_password = st.text_input("Confirme a Senha", type="password")

    if st.button("Registrar"):
        if not name or not username or not password or not confirm_password:
            st.error("Todos os campos são obrigatórios!")
        elif password != confirm_password:
            st.error("As senhas não coincidem!")
        else:
            # Faz a requisição POST para o backend para registrar o usuário
            response = requests.post(f"{API_BASE_URL}/register_user", json={
                "name": name,
                "username": username,
                "password": password
            })
            if response.status_code == 201:
                st.success("Usuário cadastrado com sucesso! Agora você pode fazer login.")
                st.session_state['login_view'] = 'login'  # Redireciona para a página de login
                st.rerun()  # Força a atualização da interface
            else:
                st.error("Erro ao cadastrar usuário. Tente outro nome de usuário.")

    # Link para voltar ao login
    if st.button("Já tenho uma conta, voltar ao login"):
        st.session_state['login_view'] = 'login'  # Redireciona para a página de login
        st.rerun()  # Força a atualização da interface

# Função para login
def login():
    st.title("Login")

    username = st.text_input("Nome de Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if username and password:
            response = requests.post(f"{API_BASE_URL}/login", json={
                "username": username,
                "password": password
            })

            if response.status_code == 200:
                data = response.json()
                st.success("Login bem-sucedido!")
                # Inicializa o estado de sessão
                st.session_state['logged_in'] = True
                st.session_state['username'] = data['username']  # Armazena o nome de usuário
                st.session_state['name'] = data['name']  # Armazena o nome completo
                st.session_state['is_admin'] = data['is_admin']  # Armazena se é admin
                # Força a atualização da interface
                st.rerun()  # Atualiza a página após o login
            else:
                st.error("Credenciais inválidas")
        else:
            st.error("Nome de usuário e senha são obrigatórios.")

    # Link para ir para a página de cadastro
    if st.button("Não tem uma conta? Cadastre-se"):
        st.session_state['login_view'] = 'register'  # Redireciona para a página de cadastro
        st.rerun()  # Força a atualização da interface

# Função para Logout
def logout():
    # Remove os dados da sessão e redefine o estado de sessão
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""
    st.session_state['name'] = ""
    st.session_state['is_admin'] = False
    st.success("Você saiu com sucesso!")
    st.rerun()  # Atualiza a página após logout

# Função para registrar o treino com upload de foto
def register_workout():
    st.title("Registrar Treino")

    # Usuário logado automaticamente
    username = st.session_state['username']

    # Faz uma requisição ao backend para obter o ID do usuário com base no username
    user_response = requests.get(f"{API_BASE_URL}/get_user_id/{username}")
    
    if user_response.status_code == 200:
        user_id = user_response.json()['user_id']
        
        # Inputs para o treino
        duration = st.number_input("Duração do Treino (em minutos)", min_value=0)
        exercise_type = st.selectbox("Tipo de Exercício", ["Corrida", "Caminhada", "Musculação", "Outros"])

        # Nível de esforço usando um slider de 1 a 10
        effort_level = st.slider(
            "Nível de Esforço do Treino (1 = Muito Fácil, 10 = Extremo)",
            min_value=1,
            max_value=10,
            value=5,  # Valor inicial
            format="%d"
        )

        # Upload de foto
        uploaded_file = st.file_uploader("Faça o upload de uma foto do treino ou evidência", type=["jpg", "jpeg", "png"])

        if st.button("Registrar Treino"):
            if duration >= 30:
                if exercise_type and effort_level:
                    if not uploaded_file:
                        st.error("O upload da foto é obrigatório!")
                    else:
                        # Dados a serem enviados ao backend
                        workout_data = {
                            "user_id": user_id,
                            "duration": int(duration),
                            "exercise_type": exercise_type,
                            "effort_level": effort_level
                        }

                        # Prepara o arquivo de foto para envio
                        files = {'file': uploaded_file.getvalue()}

                        # Faz a requisição POST para o backend para registrar o treino
                        response = requests.post(
                            f"{API_BASE_URL}/register_workout",
                            data=workout_data,
                            files=files
                        )

                        if response.status_code == 201:
                            st.success("Parabéns pelo registro do treino, continue assim!")
                        else:
                            st.error("Falha ao registrar treino.")
            else:
                st.warning("O treino deve ter no mínimo 30 minutos de duração para ser registrado.")
    else:
        st.error("Erro ao buscar ID do usuário.")
        
# Função para obter a lista de usuários
def get_usernames():
    response = requests.get(f"{API_BASE_URL}/get_usernames")
    if response.status_code == 200:
        users = response.json()['users']  # Backend agora retorna 'username' e 'name'
        return users
    else:
        st.error("Erro ao buscar nomes de usuários.")
        return []

# Função para obter a lista de grupos
def get_groups():
    response = requests.get(f"{API_BASE_URL}/get_groups")
    if response.status_code == 200:
        return response.json()['groups']  # Backend deve retornar os grupos
    else:
        st.error("Erro ao buscar grupos.")
        return []
    
# Função para obter usuários sem grupo
def get_users_without_group():
    response = requests.get(f"{API_BASE_URL}/get_users_without_group")
    if response.status_code == 200:
        return response.json()['usernames']  # Backend deve retornar os nomes de usuários sem grupo
    else:
        st.error("Erro ao buscar usuários sem grupo.")
        return []
    
# Função para gerenciar grupos
def manage_groups():
    st.title("Gerenciamento de Grupos")

    # Seção para visualização de grupos e membros
    st.header("Grupos e Membros")
    groups = get_groups()

    if groups:
        for group in groups:
            st.subheader(f"Grupo: {group['name']}")
            # Verifica se a chave 'members' está presente e exibe os nomes reais dos membros
            if 'members' in group and group['members']:
                st.write(f"Membros: {', '.join(group['members'])}")  # Agora exibindo os nomes reais
            else:
                st.write("Membros: Nenhum membro")
    else:
        st.write("Nenhum grupo disponível.")

    # Seção para visualização de usuários sem grupo
    st.header("Usuários sem Grupo")
    users_without_group = get_users_without_group()

    # Pega a lista de nomes de usuários e nomes reais
    users = get_usernames()

    # Cria um dicionário de {nome: username} para facilitar a escolha e envio
    user_options = {user['name']: user['username'] for user in users}

    # Mapeia os usuários sem grupo para seus nomes reais
    users_without_group_names = [user['name'] for user in users if user['username'] in users_without_group]

    if users_without_group_names:
        st.write(", ".join(users_without_group_names))
    else:
        st.write("Todos os usuários estão atribuídos a um grupo.")

    st.markdown("---")

    # Seção para criar e deletar grupos
    st.header("Criar ou Deletar Grupos")

    # Criar grupo
    group_name = st.text_input("Nome do Grupo")
    if st.button("Criar Grupo"):
        if group_name:
            response = requests.post(f"{API_BASE_URL}/create_group", json={"name": group_name})
            if response.status_code == 201:
                st.success(f"Grupo '{group_name}' criado com sucesso!")
                st.rerun()  # Atualiza a página
            else:
                st.error("Erro ao criar o grupo.")
        else:
            st.error("O nome do grupo é obrigatório.")

    # Deletar grupo
    groups_options = {group['name']: group['id'] for group in groups}  # Opções de grupos para deletar
    group_to_delete = st.selectbox("Selecione um grupo para deletar", list(groups_options.keys()))
    if st.button("Deletar Grupo"):
        group_id = groups_options[group_to_delete]
        response = requests.post(f"{API_BASE_URL}/delete_group", json={"group_id": group_id})
        if response.status_code == 200:
            st.success(f"Grupo '{group_to_delete}' deletado com sucesso!")
            st.rerun()  # Atualiza a página
        else:
            st.error("Erro ao deletar o grupo.")

    st.markdown("---")

    # Seção para atribuir usuário a grupo
    st.header("Atribuir Usuário a Grupo")

    # Dropdown para escolher usuário sem grupo (exibe nomes)
    if users_without_group_names:
        user_to_assign_name = st.selectbox("Selecione um usuário sem grupo", users_without_group_names)

        # Pega o username do nome selecionado
        user_to_assign_username = user_options[user_to_assign_name]

        # Dropdown para escolher grupo
        groups_for_assignment = {group['name']: group['id'] for group in groups}
        group_for_assignment = st.selectbox("Selecione um grupo para o usuário", list(groups_for_assignment.keys()))

        if st.button("Atribuir Usuário ao Grupo"):
            group_id = groups_for_assignment[group_for_assignment]
            response = requests.post(f"{API_BASE_URL}/assign_user_to_group", json={
                "username": user_to_assign_username,  # Nome do usuário (username)
                "group_id": group_id  # ID do grupo
            })
            if response.status_code == 200:
                st.success(f"Usuário {user_to_assign_name} foi atribuído ao grupo {group_for_assignment} com sucesso!")
                st.rerun()  # Atualiza a página
            else:
                st.error("Erro ao atribuir o usuário ao grupo.")
    else:
        st.write("Não há usuários sem grupo.")

# Função para visualizar desempenho e multas dinâmicas
def view_performance_and_fines_dynamic():
    st.title("Ver Desempenho e Progresso")

    # Pega a lista de nomes de usuários e usernames
    users = get_usernames()

    # Cria um dicionário de {nome: username} para facilitar a escolha e envio
    user_options = {user['name']: user['username'] for user in users}

    # Nome do usuário logado (padrão inicial)
    current_username = st.session_state['username']
    current_user_name = next(user['name'] for user in users if user['username'] == current_username)

    # Selectbox para escolher o usuário, com o nome do usuário logado como valor padrão
    selected_name = st.selectbox("Selecione o Usuário", list(user_options.keys()), index=list(user_options.values()).index(current_username))

    # Pega o `username` com base no `name` selecionado
    selected_username = user_options[selected_name]

    if selected_username:
        # Faz a requisição GET para buscar o desempenho do usuário
        response = requests.get(f"{API_BASE_URL}/user_fines_dynamic/{selected_username}")

        if response.status_code == 200:
            data = response.json()
            st.write(f"Nome: {data['name']}")
            st.write(f"Total de Multas Acumuladas: R$ {data['total_fines']}")

            # Exibir multas detalhadas por mês
            st.subheader("Detalhamento de Multas Mensais")
            fines_detail = data['fines_detail']
            for month in fines_detail:
                st.write(f"**{month['month']}**")
                for week in month['weeks']:
                    st.write(f"Semana de {week['week_start']} até {week['week_end']}:")
                    st.write(f"- Treinos: {week['workouts']}")
                    st.write(f"- Multa: R$ {week['fine']}")
                st.markdown("---")
        else:
            st.error("Erro ao buscar o desempenho do usuário.")

# Função Principal
def main():
    st.sidebar.markdown("<h1 style='text-align: center; color: white;'>Desafio Fitness</h1>", unsafe_allow_html=True)
    # Carrega a imagem local no topo da barra lateral
    st.sidebar.image(logo_path, use_column_width=True)

    # Verifica e inicializa o estado de sessão para 'logged_in', 'username', 'name' e 'is_admin'
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = ""
    if 'name' not in st.session_state:
        st.session_state['name'] = ""
    if 'is_admin' not in st.session_state:
        st.session_state['is_admin'] = False  # Define is_admin como False por padrão

    if 'login_view' not in st.session_state:
        st.session_state['login_view'] = 'login'

    # Se o usuário não estiver logado, exibe a tela de login ou cadastro com base na flag
    if not st.session_state['logged_in']:
        if st.session_state['login_view'] == 'login':
            login()
        elif st.session_state['login_view'] == 'register':
            register()
    else:
        # Se o usuário estiver logado, exibe as opções do menu
        st.sidebar.write(f"Bem-vindo, {st.session_state['name']}!")
        
        # Opções para administradores
        if st.session_state['is_admin']:
            option = st.sidebar.radio("Escolha uma página", 
                                      ("Registrar Treino", "Ver Desempenho e Progresso", 
                                       "Gerenciar Grupos"))
        else:
            # Opções para usuários comuns
            option = st.sidebar.radio("Escolha uma página", 
                                      ("Registrar Treino", "Ver Desempenho e Progresso"))

        if option == "Registrar Treino":
            register_workout()
        elif option == "Ver Desempenho e Progresso":
            view_performance_and_fines_dynamic()
        elif option == "Gerenciar Grupos" and st.session_state['is_admin']:
            manage_groups()
        
        # Adiciona espaçamento na barra lateral
        st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)

        # Adiciona o botão "Sair da conta" mais para baixo
        if st.sidebar.button("Sair da conta"):
            logout()

if __name__ == "__main__":
    main()
