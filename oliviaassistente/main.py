from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import engine, Base, get_db
import models
import auth
from core.olivia_service import gerar_resposta_olivia

# 1. Cria as tabelas na base de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Olívia Assistente API",
    description="API do Projeto Integrador Olívia Assistente",
    version="1.0"
)

# 2. CONFIGURAÇÃO COMPLETA DE CORS (OBRIGATÓRIO FICAR ANTES DOS ROUTERS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite requisições de qualquer origem (Vercel, Localhost, etc.)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 3. Registo de Routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])

# Schema de validação do Chat
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = 1
    conversation_id: Optional[int] = None

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API da Olívia está ativa!"}

@app.post("/api/chat")
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="A mensagem não pode estar vazia.")

    # 1. Recupera a conversa ou cria uma nova
    if payload.conversation_id:
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == payload.conversation_id
        ).first()
        if not conversation:
            conversation = models.Conversation(
                user_id=payload.user_id,
                title=payload.message[:30]
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
    else:
        conversation = models.Conversation(
            user_id=payload.user_id,
            title=payload.message[:30]
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 2. Guarda mensagem do utilizador
    user_msg = models.Message(
        conversation_id=conversation.id,
        role="user",
        content=payload.message
    )
    db.add(user_msg)

    # 3. Resposta da Olívia via Gemini
    try:
        resposta_texto = gerar_resposta_olivia(payload.message)
    except Exception as e:
        resposta_texto = "Olá! Tive uma pequena oscilação temporária ao conectar ao serviço Gemini. Pode tentar novamente?"

    # 4. Guarda a resposta e devolve ao frontend
    bot_msg = models.Message(
        conversation_id=conversation.id,
        role="assistant",
        content=resposta_texto
    )
    db.add(bot_msg)
    db.commit()

    return {
        "conversation_id": conversation.id,
        "response": resposta_texto
    }