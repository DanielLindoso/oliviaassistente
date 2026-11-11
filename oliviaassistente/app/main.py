from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from oliviaassistente.core.olivia_service import enviar_mensagem_gemini


app = FastAPI(
    title="Olivia Assistente",
    description="API do chatbot Olivia",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://olivia-fskx.onrender.com",
        "https://olivia-fskx.onrender.com/api/chat",
        "https://oliviacalm.vercel.app/chat.html",
        "https://oliviacalm.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/")
def health_check():
    return {
        "status": "online",
        "message": "Olivia Assistente está funcionando."
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="A mensagem não pode estar vazia."
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="A variável GEMINI_API_KEY não foi encontrada no ambiente."
        )

    # Limpeza de aspas
    texto_usuario = request.message.strip().strip('"').strip("'")

    genai.configure(api_key=api_key.strip())

    # PROMPT EMBUTIDO DIRETAMENTE NA ROTA
    prompt_completo = f"""Você é a Olívia, uma parceira de conversa empática, acolhedora e inteligente.

DIRETRIZES OBRIGATÓRIAS:
1. Escreva uma resposta humana, empática e bem desenvolvida em 2 a 4 parágrafos curtos.
2. Converse diretamente sobre o assunto mencionado (sobrecarga de prazos, ansiedade com entregas da faculdade e cursos, rotina). Dê conselhos práticos de organização e acolhimento.
3. É ESTRITAMENTE PROIBIDO oferecer ou perguntar sobre exercícios de respiração, acalmar a mente ou técnicas de relaxamento.
4. É ESTRITAMENTE PROIBIDO criar opções ou menus do tipo "prefere desabafar ou respirar?".
5. PROTOCOLO DE CRISES: Se o usuário mencionar autolesão ou ideação suicida, acolha calorosamente e forneça o contato do CVV (188) ou cvv.org.br.

Mensagem do usuário: "{texto_usuario}"

Sua resposta acolhedora e conversacional:"""

    modelos_para_testar = ["gemini-1.5-flash", "gemini-1.5-pro"]
    resposta_texto = None

    for nome_modelo in modelos_para_testar:
        try:
            model = genai.GenerativeModel(model_name=nome_modelo)
            response = model.generate_content(prompt_completo)
            if response and getattr(response, "text", None):
                resposta_texto = response.text
                break
        except Exception as e:
            print(f"Erro no modelo {nome_modelo}: {e}")
            continue

    if not resposta_texto:
        resposta_texto = "Estou recebendo muitas mensagens neste momento. Pode repetir o que disse para mim, por favor?"

    return ChatResponse(response=resposta_texto)