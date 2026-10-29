from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import engine, Base, get_db
import models
import auth
from core.olivia_service import gerar_resposta_olivia

# Cria as tabelas na base de dados automaticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Olívia Assistente API",
    description="API do Projeto Integrador Olívia Assistente",
    version="1.0"
)

# CORS liberado para o Frontend na Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REGISTRA O ROTEADOR COM O PREFIXO /auth
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])

# Schema de validação para a rota de chat
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = 1  # ID padrão enquanto o frontend implementa o login
    conversation_id: Optional[int] = None

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API da Olívia está ativa!"}

@app.post("/api/chat")
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="A mensagem não pode estar vazia.")

    # 1. Recupera a conversa existente ou cria uma nova
    if payload.conversation_id:
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == payload.conversation_id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversa não encontrada.")
    else:
        titulo_conversa = payload.message[:30] + "..." if len(payload.message) > 30 else payload.message
        conversation = models.Conversation(
            user_id=payload.user_id,
            title=titulo_conversa
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # 2. Persiste a mensagem enviada pelo utilizador
    user_msg = models.Message(
        conversation_id=conversation.id,
        role="user",
        content=payload.message
    )
    db.add(user_msg)

    # 3. Gera a resposta através do serviço Gemini (Olívia)
    try:
        resposta_texto = gerar_resposta_olivia(payload.message)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Ocorreu uma instabilidade ao conectar com a Olívia. Tente novamente em instantes."
        )

    # 4. Persiste a resposta da assistente
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