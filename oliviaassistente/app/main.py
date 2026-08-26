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
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="A mensagem não pode estar vazia."
        )

    resposta = enviar_mensagem_gemini(request.message)

    return ChatResponse(response=resposta)