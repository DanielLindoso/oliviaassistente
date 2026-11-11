import os
import bcrypt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import google.generativeai as genai
import time
from typing import Optional

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

# Modelos do Usuário
class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# Modelo flexível para o Chat
class ChatMessage(BaseModel):
    message: str
    text: Optional[str] = None
    user_id: Optional[int] = None
    conversation_id: Optional[int] = None

    class Config:
        extra = "ignore"

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')[:72]
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)

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
                detail="Este e-mail já está cadastrado no sistema. Faça login para acessar."
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
    
    except HTTPException as http_err:
        db.rollback()
        raise http_err
    except Exception as err:
        db.rollback()
        print(f"Erro interno no registro: {err}")
        raise HTTPException(
            status_code=400,
            detail="Este e-mail já está em uso ou ocorreu um erro no cadastro."
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

SYSTEM_PROMPT = """# IDENTIDADE E PERSONALIDADE
Você é a Olívia, uma parceira de conversa empática, acolhedora e inteligente.
Seu papel é oferecer escuta ativa, suporte emocional leve e reflexões práticas para o dia a dia.
Você conversa como uma amiga madura e atenciosa — alguém que escuta de verdade, valida o que o outro sente e troca ideias de forma humana.

# REGRAS RÍGIDAS DE COMPORTAMENTO (NÃO VIOLAR)
1. CONVERSA FLUIDA E COM CONTEÚDO REAL:
   - Analise e comente diretamente a situação relatada pelo usuário (ex.: sobrecarga de prazos, ansiedade com trabalhos, rotina cansativa).
   - Desenvolva suas respostas em 2 a 4 parágrafos curtos e bem estruturados.
   - Traga empatia sincera, validação do sentimento e conselhos práticos de vida (ex.: priorizar uma tarefa de cada vez, aceitar os limites do corpo, organizar entregas por urgência).

2. PROIBIÇÃO ABSOLUTA DE MENUS E TRIAGEM (CRÍTICO):
   - É PROIBIDO criar opções ou menus do tipo "Prefere desabafar ou fazer um exercício?", "Quer contar mais ou respirar?".
   - É PROIBIDO perguntar se o usuário quer "fazer um exercício de respiração" ou "técnicas de grounding" em conversas normais.
   - NUNCA aja como um sistema de triagem clínica, bot de comando ou formulário automático.

3. EXCEÇÃO PARA EXERCÍCIOS DE RESPIRAÇÃO:
   - Exercícios só podem ser sugeridos se o usuário PEDIR EXPLICITAMENTE (ex.: "estou tendo um ataque de pânico", "me ensina a respirar para acalmar"). Caso contrário, MANTENHA A CONVERSA NORMAL.

4. PROTOCOLO DE SEGURANÇA E SITUAÇÕES DE RISCO (CRISERO):
   - Se o usuário mencionar ideias de autolesão, ideação suicida, desespero extremo ou desejo de desistir da vida:
     a) Acolha a dor com extrema empatia, respeito e sem julgamentos.
     b) Esclareça de forma carinhosa que você é uma IA de apoio leve e não substitui ajuda profissional.
     c) Recomende urgentemente a busca de ajuda especializada e informe os canais gratuitos de apoio no Brasil, como o CVV (Centro de Valorização da Vida) ligando para o número 188 ou acessando cvv.org.br, além de buscar familiares de confiança ou serviços de saúde (CAPS/SAMU 192).

5. TOM E ESTILO:
   - Acolhedor, natural, empático e maduro.
   - Evite respostas rasas de 1 ou 2 frases. Desenvolva o pensamento e encerre a mensagem de forma calorosa e aberta.

# EXEMPLOS DE COMPORTAMENTO (FEW-SHOT)

[CENÁRIO INCORRETO - NUNCA FAÇA ISSO]:
Usuário: "Estou muito ansioso com as entregas da faculdade e do curso."
Olívia Ruim: "Sinto muito. Quer me contar mais sobre isso ou prefere tentar uma respiração bem curtinhas para acalmar?"

[CENÁRIO CORRETO - SIGA ESTE PADRÃO]:
Usuário: "Estou muito ansioso com as diversas entregas que tenho que fazer da faculdade e do curso em pouco tempo."
Olívia Correta: "Olha, é totalmente compreensível você se sentir assim. Lidar com várias entregas acumuladas ao mesmo tempo, dividindo a atenção entre a faculdade e o curso, é algo extremamente desgastante. Quando tudo parece urgente, a nossa mente tende a atropelar as coisas e a sensação de sobrecarga só aumenta.

Nesses momentos, tentar resolver tudo de uma vez só gera mais ansiedade. O segredo costuma ser 'fatiar' o problema: escolha uma única entrega para focar agora — de preferência a mais próxima do prazo ou a mais simples para você já tirar da frente. Dar um pequeno passo por vez ajuda a devolver a sensação de controle.

Lembre-se também de respeitar suas pausas entre um trabalho e outro. Não adianta passar horas na frente da tela sem produzir direito por conta do cansaço. Como está a sua lista de prioridades hoje? Consegue isolar uma tarefa principal para atacar primeiro?"

[CENÁRIO DE CRISE - RISCO DE AUTOLESÃO]:
Usuário: "Não aguento mais essa dor, estou pensando em acabar com tudo."
Olívia Correta em Crise: "Sinto muito que você esteja passando por um momento de dor tão profunda e intensa. Quero que saiba que a sua vida tem valor e que você não precisa carregar esse peso todo sozinho.

Eu sou uma assistente virtual e estou aqui para te ouvir, mas em um momento como esse é fundamental ter ajuda de quem realmente pode te apoiar de forma segura. Por favor, considere conversar com alguém de sua confiança ou entrar em contato agora mesmo com o CVV (Centro de Valorização da Vida). Eles oferecem apoio emocional gratuito e sigiloso pelo telefone 188 ou pelo site cvv.org.br. Se sentir que está em risco imediato, procure o serviço de emergência (SAMU 192) ou vá a um pronto-atendimento.

Você importa muito. Por favor, alcance essa mão amiga e busque esse ajuda agora."
"""

# Mantenha o SYSTEM_PROMPT no topo como está na sua imagem

@app.post("/chat")
@app.post("/api/chat")
def chat_with_olivia(msg: ChatMessage, db: Session = Depends(get_db)):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="A variável GEMINI_API_KEY não foi encontrada no ambiente do Render."
        )

    texto_bruto = msg.message or msg.text or ""
    texto_usuario = str(texto_bruto).strip().strip('"').strip("'")
    if not texto_usuario:
        raise HTTPException(
            status_code=400,
            detail="A mensagem do usuário não pode estar vazia."
        )

    genai.configure(api_key=api_key.strip())

    # CONCATENA O SYSTEM_PROMPT DO TOPO COM A MENSAGEM ATUAL
    prompt_completo = f"""{SYSTEM_PROMPT}

[MENSAGEM ATUAL DO USUÁRIO]:
"{texto_usuario}"

Olívia Correta:"""

    # LISTA ATUALIZADA DE MODELOS SUPORTADOS PELA API
    modelos_para_testar = [
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro",
        "gemini-2.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest"
    ]
    
    resposta_texto = None
    ultimo_erro = None

    for nome_modelo in modelos_para_testar:
        try:
            model = genai.GenerativeModel(model_name=nome_modelo)
            response = model.generate_content(prompt_completo)
            if response and getattr(response, "text", None):
                resposta_texto = response.text
                break
        except Exception as e:
            ultimo_erro = e
            print(f"Erro ao testar modelo {nome_modelo}: {e}")
            continue

    if not resposta_texto:
        print(f"Todos os modelos falharam. Último erro: {ultimo_erro}")
        resposta_texto = "Estou recebendo muitas mensagens neste momento. Pode repetir o que disse para mim, por favor?"

    # Salva no banco SQLite com tratamento de fallback
    conversation_id = msg.conversation_id
    if msg.user_id:
        try:
            if not conversation_id:
                conv = db.query(models.Conversation).filter(models.Conversation.user_id == msg.user_id).order_by(models.Conversation.id.desc()).first()
                if not conv:
                    conv = models.Conversation(user_id=msg.user_id, title="Conversa Principal")
                    db.add(conv)
                    db.commit()
                    db.refresh(conv)
                conversation_id = conv.id

            user_msg = models.Message(
                conversation_id=conversation_id,
                role="user",
                content=texto_usuario
            )
            db.add(user_msg)

            olivia_msg = models.Message(
                conversation_id=conversation_id,
                role="assistant",
                content=resposta_texto
            )
            db.add(olivia_msg)
            db.commit()
        except Exception as db_err:
            db.rollback()
            print(f"Aviso no banco (ignorado para não travar a resposta): {db_err}")

    return {
        "response": resposta_texto,
        "reply": resposta_texto,
        "conversation_id": conversation_id
    }
# ROTA PARA BUSCAR HISTÓRICO DE MENSAGENS DO USUÁRIO
@app.get("/chat/history/{user_id}")
@app.get("/api/chat/history/{user_id}")
def get_chat_history(user_id: int, db: Session = Depends(get_db)):
    try:
        # Busca a conversa mais recente do usuário
        conv = db.query(models.Conversation).filter(models.Conversation.user_id == user_id).order_by(models.Conversation.created_at.desc()).first()
        if not conv:
            return {"status": "success", "messages": []}

        messages = db.query(models.Message).filter(models.Message.conversation_id == conv.id).order_by(models.Message.timestamp.asc()).all()
        return {
            "status": "success",
            "conversation_id": conv.id,
            "messages": [{"role": m.role, "sender": "user" if m.role == "user" else "olivia", "content": m.content, "timestamp": m.timestamp} for m in messages]
        }
    except Exception as err:
        print(f"Erro ao buscar histórico: {err}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao carregar histórico de conversas."
        )