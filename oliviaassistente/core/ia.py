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

# Inicializa o cliente moderno passando a chave explicitamente
client = genai.Client(api_key=API_GEMINI)

def explain_ai_short() -> str:
    """Retorna uma resposta de teste do Gemini."""
    try:
        # Usando o modelo atualizado e estável
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Diga 'Olá Mundo' em português para testar a conexão.",
        )
        return getattr(response, "text", str(response))
    except Exception as e:
        return f"Erro na API do Gemini: {e}"

if __name__ == "__main__":
    print(explain_ai_short())