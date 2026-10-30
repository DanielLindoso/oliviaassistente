from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from database import engine, Base, get_db
import models
import auth
from core.olivia_service import gerar_resposta_olivia

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Olívia Assistente API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# No main.py
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(auth.router, tags=["Autenticação Direta"])

# Schemas Pydantic
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = 1
    conversation_id: Optional[int] = None

class TaskCreate(BaseModel):
    title: str
    user_id: Optional[int] = 1

class TaskUpdate(BaseModel):
    completed: bool

class MoodCreate(BaseModel):
    mood: str
    user_id: Optional[int] = 1

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API da Olívia está ativa com suporte a Banco de Dados!"}

# ROTAS DE CHAT
@app.post("/api/chat")
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Mensagem vazia.")

    if payload.conversation_id:
        conversation = db.query(models.Conversation).filter(models.Conversation.id == payload.conversation_id).first()
        if not conversation:
            conversation = models.Conversation(user_id=payload.user_id, title=payload.message[:30])
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
    else:
        conversation = models.Conversation(user_id=payload.user_id, title=payload.message[:30])
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    user_msg = models.Message(conversation_id=conversation.id, role="user", content=payload.message)
    db.add(user_msg)

    try:
        resposta_texto = gerar_resposta_olivia(payload.message)
    except Exception:
        resposta_texto = "Olá! Tive uma pequena oscilação temporária na conexão. Pode repetir?"

    bot_msg = models.Message(conversation_id=conversation.id, role="assistant", content=resposta_texto)
    db.add(bot_msg)
    db.commit()

    return {"conversation_id": conversation.id, "response": resposta_texto}

# ROTAS DE TAREFAS (PERSISTENTES)
@app.get("/api/tasks/{user_id}")
def get_tasks(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.Task).filter(models.Task.user_id == user_id).all()

@app.post("/api/tasks")
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    new_task = models.Task(user_id=payload.user_id, title=payload.title)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.put("/api/tasks/{task_id}")
def toggle_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    task.completed = payload.completed
    db.commit()
    return task

# ROTAS DE DIÁRIO DE HUMOR
@app.post("/api/mood")
def log_mood(payload: MoodCreate, db: Session = Depends(get_db)):
    mood_entry = models.MoodLog(user_id=payload.user_id, mood=payload.mood)
    db.add(mood_entry)
    db.commit()
    return {"status": "success", "message": "Humor registrado no banco!"}