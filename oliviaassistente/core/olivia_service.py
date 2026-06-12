import os
from google import genai
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Puxa a chave do ambiente
API_GEMINI = os.getenv("GEMINI_API_KEY")

if not API_GEMINI:
    raise RuntimeError(
        "Chave GEMINI_API_KEY não encontrada no arquivo .env."
    )

# Inicializa o cliente moderno do Gemini
client = genai.Client(api_key=API_GEMINI)

def enviar_mensagem_gemini(mensagem_usuario: str) -> str:
    """Envia a mensagem do usuário para a Olivia (Gemini) e retorna a resposta."""
    try:
        # Configura o comportamento e a personalidade da Olivia
        prompt_sistema = (
            "Você é a Olivia, uma assistente virtual prestativa, inteligente e amigável. "
            "Responda sempre em português de forma clara."
        )
        
        # Faz a chamada para o modelo moderno gemini-2.5-flash
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{prompt_sistema}\n\nUsuário: {mensagem_usuario}\nOlivia:",
        )
        
        # Retorna o texto gerado de forma segura
        return getattr(response, "text", str(response))
        
    except Exception as e:
        return f"[Olivia]: Erro na API do Gemini: {e}"