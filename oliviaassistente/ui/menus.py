# Caminho do arquivo: ui/menus.py

from ui.utils import exibir_cabecalho
import core.olivia_service as olivia_service
# Importando as novas funções que interagem direto com o MySQL
from data.data_manager import (
    inserir_usuario, 
    inserir_humor, 
    criar_conversa, 
    inserir_mensagem, 
    registrar_exercicio_concluido,
    inserir_avaliacao_ansiedade
)

def criar_usuario_menu(dados_mock=None):
    """Chama a inserção direta no banco de dados MySQL"""
    exibir_cabecalho("CRIAR PERFIL OLIVIA 💜")
    # A lógica de pedir o nome e gerar os dados automáticos agora roda dentro de inserir_usuario()
    inserir_usuario()
    input("\nPressione Enter para voltar ao menu principal.")


def registro_humor_menu(id_usuario_logado: int):
    """Registra o humor do usuário diretamente no MySQL"""
    while True:
        exibir_cabecalho("REGISTRO DE HUMOR 😊")
        print("1. Registrar Novo Humor")
        print("2. Voltar")
        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            # Chama a função do banco passando o ID do usuário conectado
            inserir_humor(id_usuario_logado)
            input("\nPressione Enter para continuar...")
        elif opcao == "2":
            break


def exercicios_ansiedade_menu(id_usuario_logado: int):
    """Menu adaptado para carregar exercícios e salvar a realização no banco de dados"""
    while True:
        exibir_cabecalho("EXERCÍCIOS PARA ANSIEDADE 💆")
        
        # Lista simulando os IDs reais da tabela 'exercicio' do seu banco
        exercicios = [
            {"id": 1, "nome": "Respiração profunda 4-4-4"},
            {"id": 2, "nome": "Meditação rápida de 2 minutos"},
            {"id": 3, "nome": "Alongamento corporal"},
            {"id": 4, "nome": "Escrever pensamentos positivos"},
            {"id": 5, "nome": "Ouvir música relaxante"}
        ]

        print("\nExercícios disponíveis:\n")
        for ex in exercicios:
            print(f"{ex['id']}. {ex['nome']}")
        print("\n" + "-" * 30)
        print("1. Marcar exercício realizado")
        print("2. Registrar Avaliação de Ansiedade Geral")
        print("3. Voltar")
        
        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            try:
                escolha = int(input("Digite o número do exercício concluído: "))
                # Valida se a escolha faz parte da nossa lista
                if 1 <= escolha <= len(exercicios):
                    registrar_exercicio_concluido(id_usuario_logado, escolha)
                else:
                    print("Exercício inválido.")
                input("\nPressione Enter...")
            except ValueError:
                input("\nOpção inválida. Pressione Enter.")
                
        elif opcao == "2":
            # Aproveita a tabela avaliacao_ansiedade criada no seu script SQL
            inserir_avaliacao_ansiedade(id_usuario_logado)
            input("\nPressione Enter...")
            
        elif opcao == "3":
            break


def painel_olivia_menu(id_usuario_logado: int):
    """Chat em tempo real integrado com a API do Gemini e gravando histórico no MySQL"""
    exibir_cabecalho("OLIVIA - ASSISTENTE EMOCIONAL 💜")
    print("Converse com Olivia sobre emoções, ansiedade e bem-estar.")
    print("Digite 'sair' para retornar.\n")

    # 1. Cria uma nova sessão na tabela 'conversa' para agrupar as mensagens deste chat
    id_conversa_ativa = criar_conversa(id_usuario_logado)
    
    if not id_conversa_ativa:
        input("Erro ao iniciar chat com o banco de dados. Pressione Enter.")
        return

    while True:
        pergunta = input("\nVocê: ").strip()

        if pergunta.lower() == "sair":
            break
        if not pergunta:
            continue

        print("\n💜 Olivia está pensando...\n")

        # 2. Envia o texto digitado pelo usuário para a função corrigida do Gemini
        resposta_olivia = olivia_service.enviar_mensagem_gemini(pergunta)

        print(f"\n[Olivia]: {resposta_olivia}")

        # 3. Registra as interações (mensagens) respeitando os ENUM ('usuario', 'olivia') do banco
        # Usamos uma lógica interna simplificada para salvar sem pedir novos inputs na hora de gravar
        import mysql.connector
        conexao = mysql.connector.connect(host='localhost', database='olivia_db', user='root', password='Senac2026')
        cursor = conexao.cursor()
        try:
            # Insere a fala do usuário
            cursor.execute("INSERT INTO mensagem (id_conversa, remetente, mensagem) VALUES (%s, 'usuario', %s)", (id_conversa_ativa, pergunta))
            # Insere a resposta do Gemini
            cursor.execute("INSERT INTO mensagem (id_conversa, remetente, mensagem) VALUES (%s, 'olivia', %s)", (id_conversa_ativa, resposta_olivia))
            conexao.commit()
        except Exception as e:
            print(f"[Erro de Log]: Não foi possível salvar as mensagens no histórico do MySQL: {e}")
        finally:
            cursor.close()
            conexao.close()

        print("\n" + "-" * 30)


def painel_principal_menu(id_usuario_logado: int, nome_usuario: str):
    """Painel logado adaptado para enviar IDs numéricos do MySQL às funções filhas"""
    while True:
        exibir_cabecalho(f"OLIVIA 💜 | Usuário: {nome_usuario} (ID: {id_usuario_logado})")
        print("1. Registro de Humor")
        print("2. Exercícios para Ansiedade")
        print("3. 💜 Conversar com Olivia")
        print("4. Logout")
        
        opcao = input("\nEscolha: ").strip()

        if opcao == "1":
            registro_humor_menu(id_usuario_logado)
        elif opcao == "2":
            exercicios_ansiedade_menu(id_usuario_logado)
        elif opcao == "3":
            painel_olivia_menu(id_usuario_logado)
        elif opcao == "4":
            break