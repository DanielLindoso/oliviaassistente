# Caminho do arquivo: data/data_manager.py

import mysql.connector
from mysql.connector import Error

# ==========================================
# CONFIGURAÇÃO DA CONEXÃO CENTRALIZADA
# ==========================================
def obter_conexao():
    return mysql.connector.connect(
        host='localhost',
        database='olivia_db',
        user='root',
        password='Senac2026'
    )

# ==========================================
# 1. TABELA: usuario
# ==========================================
# Substitua apenas essa função dentro de data/data_manager.py

def inserir_usuario():
    print("\n--- Cadastrar Novo Usuário ---")
    nome = input("Nome do usuário: ").strip()
    
    if not nome:
        print("Erro: O nome é obrigatório!")
        return

    # AGORA O PROGRAMA PERGUNTA AO USUÁRIO:
    email = input("Digite o seu e-mail: ").strip()
    senha = input("Digite uma senha: ").strip()
    data_nascimento = input("Digite sua data de nascimento (Ano-Mês-Dia, ex: 2005-08-20): ").strip()

    # Validações simples para evitar erros no banco
    if not email or not senha or not data_nascimento:
        print("\n[Erro] Todos os campos são obrigatórios para o cadastro!")
        return

    conexao = obter_conexao()
    cursor = conexao.cursor()
    try:
        comando = """
            INSERT INTO usuario (nome, email, senha_hash, data_nascimento, email_verificado) 
            VALUES (%s, %s, %s, %s, TRUE)
        """
        # Passando as variáveis que o usuário digitou
        cursor.execute(comando, (nome, email, senha, data_nascimento))
        conexao.commit()
        print(f"\n[Sucesso] Perfil de '{nome}' cadastrado com sucesso! ID gerado: {cursor.lastrowid}")
    except Error as e:
        print(f"Erro ao inserir usuário no MySQL: {e}")
    finally:
        cursor.close()
        conexao.close()

# ==========================================
# 2. TABELA: humor
# ==========================================
def inserir_humor(id_usuario_logado):
    try:
        nivel_humor = int(input("Nível do humor (1 a 5): "))
    except ValueError:
        print("Erro: O nível de humor precisa ser um número inteiro!")
        return

    observacao = input("Observação/Como se sente: ").strip()

    conexao = obter_conexao()
    cursor = conexao.cursor()
    try:
        comando = "INSERT INTO humor (id_usuario, nivel_humor, observacao) VALUES (%s, %s, %s)"
        cursor.execute(comando, (id_usuario_logado, nivel_humor, observacao))
        conexao.commit()
        print("\n[Sucesso] Registro de humor salvo!")
    except Error as e:
        print(f"Erro ao inserir humor: {e}")
    finally:
        cursor.close()
        conexao.close()

# ==========================================
# 3. TABELA: conversa
# ==========================================
def criar_conversa(id_usuario_logado):
    """Cria uma nova sessão de chat/conversa para o usuário"""
    conexao = obter_conexao()
    cursor = conexao.cursor()
    id_conversa_gerada = None
    try:
        comando = "INSERT INTO conversa (id_usuario) VALUES (%s)"
        cursor.execute(comando, (id_usuario_logado,))
        conexao.commit()
        id_conversa_gerada = cursor.lastrowid
    except Error as e:
        print(f"Erro ao criar conversa: {e}")
    finally:
        cursor.close()
        conexao.close()
    return id_conversa_gerada

# ==========================================
# 4. TABELA: mensagem
# ==========================================
def inserir_mensagem(id_conversa_ativa, remetente):
    """remetente deve ser 'usuario' ou 'olivia'"""
    mensagem = input(f"[{remetente.upper()}] Digite a mensagem: ").strip()   
    
    if not mensagem:
        print("Erro: A mensagem não pode estar vazia!")
        return

    conexao = obter_conexao()
    cursor = conexao.cursor()
    try:
        comando = "INSERT INTO mensagem (id_conversa, remetente, mensagem) VALUES (%s, %s, %s)"
        cursor.execute(comando, (id_conversa_ativa, remetente, mensagem))
        conexao.commit()
    except Error as e:
        print(f"Erro ao salvar mensagem: {e}")
    finally:
        cursor.close()
        conexao.close()

# ==========================================
# 5. TABELA: exercicio
# ==========================================
def inserir_exercicio():
    print("\n--- Cadastrar Novo Exercício Mente/Corpo ---")
    titulo = input("Título do exercício: ").strip()
    descricao = input("Descrição / Passo a passo: ").strip()
    categoria = input("Categoria (Ex: Respiração, Meditação): ").strip()

    if not titulo:
        print("Erro: O título é obrigatório!")
        return

    conexao = obter_conexao()
    cursor = conexao.cursor()
    try:
        comando = "INSERT INTO exercicio (titulo, descricao, categoria) VALUES (%s, %s, %s)"
        cursor.execute(comando, (titulo, descricao, categoria))
        conexao.commit()
        print(f"\n[Sucesso] Exercício '{titulo}' adicionado à biblioteca!")
    except Error as e:
        print(f"Erro ao cadastrar exercício: {e}")
    finally:
        cursor.close()
        conexao.close()

# ==========================================
# 6. TABELA: exercicio_realizado
# ==========================================
def registrar_exercicio_concluido(id_usuario_logado, id_exercicio_escolhido):
    """Registra que o usuário completou uma atividade específica"""
    conexao = obter_conexao()
    cursor = conexao.cursor()
    try:
        comando = "INSERT INTO exercicio_realizado (id_usuario, id_exercicio) VALUES (%s, %s)"
        cursor.execute(comando, (id_usuario_logado, id_exercicio_escolhido))
        conexao.commit()
        print("\n[Sucesso] Atividade marcada como concluída e salva no seu histórico.")
    except Error as e:
        print(f"Erro ao salvar histórico do exercício: {e}")
    finally:
        cursor.close()
        conexao.close()

# ==========================================
# 7. TABELA: avaliacao_ansiedade
# ==========================================
def inserir_avaliacao_ansiedade(id_usuario_logado):
    try:
        nivel_ansiedade = int(input("Como está sua ansiedade hoje (1-Pouca a 10-Muita): "))
    except ValueError:
        print("Erro: O nível de ansiedade precisa ser um número inteiro!")
        return

    observacao = input("Gostaria de detalhar o que está sentindo? ").strip()

    conexao = obter_conexao()
    cursor = conexao.cursor()
    try:
        comando = "INSERT INTO avaliacao_ansiedade (id_usuario, nivel_ansiedade, observacao) VALUES (%s, %s, %s)"
        cursor.execute(comando, (id_usuario_logado, nivel_ansiedade, observacao))
        conexao.commit()
        print("\n[Sucesso] Avaliação de ansiedade salva!")
    except Error as e:
        print(f"Erro ao salvar avaliação: {e}")
    finally:
        cursor.close()
        conexao.close()