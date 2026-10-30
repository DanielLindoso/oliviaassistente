from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext

from database import engine, Base, get_db
import models

# Garante a criação de todas as tabelas na base de dados
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Erro ao criar tabelas: {e}")

app = FastAPI(title="Olívia Assistente API", version="1.0")

# Permite requisições de qualquer origem (Vercel, Localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

def get_password_hash(password: str):
    # Trunca a palavra-passe para no máximo 72 bytes para evitar exceção do bcrypt
    password_bytes = password.encode('utf-8')[:72]
    return pwd_context.hash(password_bytes.decode('utf-8', errors='ignore'))

def verify_password(plain_password: str, hashed_password: str):
    password_bytes = plain_password.encode('utf-8')[:72]
    return pwd_context.verify(password_bytes.decode('utf-8', errors='ignore'), hashed_password)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API da Olívia está ativa!"}

@app.post("/auth/register")
@app.post("/register")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(models.User).filter(models.User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400, 
                detail="Este e-mail já está cadastrado no sistema."
            )

        hashed_pw = get_password_hash(user.password)
        
        # Criação do utilizador na tabela
        new_user = models.User(
            name=user.name, 
            email=user.email, 
            password_hash=hashed_pw
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"status": "success", "message": "Usuário cadastrado com sucesso!"}
    
    except HTTPException as http_err:
        raise http_err
    except Exception as err:
        db.rollback()
        print(f"Erro interno no registro: {err}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno no servidor: {str(err)}"
        )

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