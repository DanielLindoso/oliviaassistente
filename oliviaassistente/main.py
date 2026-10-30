from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext

from oliviaassistente.database import engine, Base, get_db
from oliviaassistente import models

# Inicializa o banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Olívia Assistente API", version="1.0")

# Configuração total do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Schemas de Autenticação
class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# Função auxiliar de senha
def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API da Olívia está ativa!"}

# ROTAS DE AUTENTICAÇÃO (Mapeadas em todas as variações possíveis)
@app.post("/auth/register")
@app.post("/register")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="Este e-mail já está cadastrado no sistema."
        )

    hashed_pw = get_password_hash(user.password)
    new_user = models.User(
        name=user.name, 
        email=user.email, 
        password_hash=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"status": "success", "message": "Usuário cadastrado com sucesso!"}

@app.post("/auth/login")
@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=401, 
            detail="E-mail ou senha incorretos."
        )

    return {
        "user_id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "access_token": f"token_{db_user.id}"
    }

# ROTA DE CHAT
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = 1
    conversation_id: Optional[int] = None

@app.post("/api/chat")
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    from core.olivia_service import gerar_resposta_olivia

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