# Caminho do arquivo: main.py (Substitua completamente o conteúdo anterior)

import mysql.connector
from ui.menus import criar_usuario_menu, painel_principal_menu
from ui.utils import exibir_cabecalho

def buscar_usuarios_no_banco():
    """Busca ID e Nome de todos os usuários diretamente no MySQL"""
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            database='olivia_db',
            user='root',
            password='Senac2026'
        )
        cursor = conexao.cursor()
        cursor.execute("SELECT id_usuario, nome FROM usuario")
        resultados = cursor.fetchall()  # Retorna uma lista de tuplas [(1, 'Daniel'), (2, 'Maria')]
        return resultados
    except Exception as e:
        print(f"\n[Erro] Não foi possível carregar os dados do MySQL: {e}")
        return []
    finally:
        if 'conexao' in locals() and conexao.is_connected():
            cursor.close()
            conexao.close()

def executar_sistema():
    while True:
        # Busca a lista atualizada de usuários no banco de dados
        usuarios = buscar_usuarios_no_banco()
        # Isolamos apenas os nomes para fins de exibição na tela
        nomes_cadastrados = [u[1] for u in usuarios]

        exibir_cabecalho("OLIVIA - ASSISTENTE VIRTUAL 💜")
        print('1. Entrar.')
        print('2. Criar conta.')
        print('3. Encerrar aplicativo.')
 
        opcao = input("\nEscolha uma opção: ").strip()
 
        if opcao == "1":
            if not usuarios:
                input("\nNenhum usuário cadastrado ainda no MySQL! Pressione Enter...")
                continue
            
            print("\nUsuários cadastrados no Banco de Dados:")
            for nome in nomes_cadastrados:
                print(f"- {nome}")
                
            nome_login = input("\nDigite seu nome para entrar: ").strip()
            
            # Percorre a lista do MySQL para encontrar o ID correto de quem está logando
            usuario_encontrado = None
            for id_banco, nome_banco in usuarios:
                if nome_banco.lower() == nome_login.lower():
                    usuario_encontrado = (id_banco, nome_banco)
                    break
            
            if usuario_encontrado:
                id_logado, nome_logado = usuario_encontrado
                print(f"\nConectando... Bem-vindo(a), {nome_logado}!")
                # Passa o ID numérico e o Nome para o painel principal do menus.py atualizado
                painel_principal_menu(id_logado, nome_logado)
            else:
                input("\nUsuário não encontrado no banco! Pressione Enter...")
                
        elif opcao == "2":
            # Abre a tela de criação onde o data_manager cuidará do resto
            criar_usuario_menu()
            
        elif opcao == "3":
            print("\nAté logo! Olivia deseja uma ótima jornada 💜")
            break
            
        else:
            input("\nOpção inválida! Pressione Enter...")

if __name__ == "__main__":
    executar_sistema()