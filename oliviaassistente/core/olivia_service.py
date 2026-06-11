from google import genai
from google.genai import types

# Coloque sua chave aqui dentro das aspas
MINHA_CHAVE = "AQ.Ab8RN6KBSZltwX1iA5pqAvatLmROjisDTKBZjKipXZAeN7vT9w"

# Inicializamos o cliente passando a chave DIRETAMENTE
client = genai.Client(api_key=MINHA_CHAVE)
MODELO_GEMINI = "gemini-2.5-flash"

def enviar_mensagem_gemini(mensagem_texto):
    """Função padrão para enviar mensagens para a Olivia"""
    try:
        response = client.models.generate_content(
            model=MODELO_GEMINI,
            contents=mensagem_texto
        )
        return response.text
    except Exception as e:
        return f"Erro na API do Gemini: {e}"
def obter_resposta_ia(Com: str, estilo_usuario: str) -> list:
    """
    Conecta ao Gemini para responder à mensagem ('Com'), adaptando-se 
    dinamicamente ao estilo do usuário (direto ou acolhedor).
    Retorna uma lista de strings.
    """
    
    # Criamos a regra de comportamento (System Instruction) com base no estilo
    if estilo_usuario == "direto":
        instrucao_sistema = (
            "Você é um assistente focado em produtividade e foco. "
            "Sua resposta DEVE ser estritamente uma lista de 2 ou 3 ações práticas, "
            "diretas, curtas e sem enrolação. Comece cada linha com 'Ação X:' ou 'Passo X:'."
        )
    else:
        # Estilo padrão / acolhedor
        instrucao_sistema = (
            "Você é um assistente empático, acolhedor e focado em bem-estar emocional. "
            "Sua resposta deve demonstrar validação sentimental, apoio e usar um tom caloroso. "
            "Pode usar emojis de forma sutil. Divida sua resposta em 2 ou 3 frases/parágrafos curtos."
        )

    try:
        # Chamada para o Gemini
        response = client.models.generate_content(
            model=MODELO_GEMINI,
            contents=Com,
            config=types.GenerateContentConfig(
                system_instruction=instrucao_sistema,
                temperature=0.7
            )
        )
        
        # Transforma a resposta de texto corrido em uma lista de strings
        linhas_resposta = [linha.strip() for linha in response.text.split("\n") if linha.strip()]
        return linhas_resposta

    except Exception as e:
        # Caso ocorra algum erro na API, retorna um fallback seguro para não quebrar o app
        print(f"Erro na API do Gemini: {e}")
        if estilo_usuario == "direto":
            return ["Erro ao conectar. Tente novamente.", "Verifique sua conexão."]
        return ["Ops, tive um probleminha para processar isso agora. 💜", "Pode tentar de novo em instantes?"]


def gerar_passos_tarefas(titulo_tarefa: str) -> list:
    """Usa o Gemini para quebrar tarefas complexas em subtarefas sequenciais."""
    
    instrucao_sistema = (
        "Você é um especialista em gerenciamento de tempo e neurodiversidade. "
        "Sua missão é quebrar a tarefa enviada pelo usuário em exatamente 3 passos sequenciais, "
        "simples e fáceis de digerir para evitar o bloqueio mental. "
        "Não adicione textos de introdução ou conclusão. Retorne apenas os 3 passos."
    )
    
    try:
        response = client.models.generate_content(
            model=MODELO_GEMINI,
            contents=f"Quebre esta tarefa em passos: {titulo_tarefa}",
            config=types.GenerateContentConfig(system_instruction=instrucao_sistema)
        )
        
        passos = [linha.strip() for linha in response.text.split("\n") if linha.strip()]
        return passos
        
    except Exception as e:
        print(f"Erro ao gerar passos: {e}")
        return ["Organizar o espaço de trabalho", "Iniciar a atividade por 15 minutos", "Fazer uma pausa"]


# --- EXEMPLO DE USO ---
if __name__ == "__main__":
    # Testando o Caso 1 (Triste) - No estilo Direto
    print("--- Teste Direto ---")
    resposta_direta = obter_resposta_ia("Estou me sentindo muito triste e mal hoje", "direto")
    for item in resposta_direta:
        print(item)
        
    print("\n--- Teste Acolhedor ---")
    # Testando o Caso 2 (Ansiedade) - No estilo Acolhedor
    resposta_acolhedora = obter_resposta_ia("Estou muito ansiosa com a prova de amanhã", "acolhedor")
    for item in resposta_acolhedora:
        print(item)

    print("\n--- Teste Quebra de Tarefas ---")
    # Testando a geração de passos para uma tarefa real
    passos_projeto = gerar_passos_tarefas("Estudar para a prova de cálculo de amanhã")
    for i, passo in enumerate(passos_projeto, 1):
        print(f"{i}. {passo}")