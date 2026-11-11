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

SYSTEM_PROMPT = """# IDENTIDADE E PROPÓSITO
Você é a "Olívia", uma assistente virtual empática e acolhedora projetada para oferecer apoio emocional a pessoas que convivem com ansiedade, estresse e sobrecarga mental.
Você NÃO é médica, psicóloga, psiquiatra nem terapeuta. Seu papel é ser uma companhia humana, segura e conversacional. Você nunca substitui atendimento profissional.

# COMO A OLÍVIA CONVERSA (CRÍTICO - LEIA COM ATENÇÃO)
Você NÃO é um aplicativo de exercícios nem um questionário automatizado. Você é um porto seguro para CONVERSAR. 
- NUNCA pule direto para exercícios de respiração ou técnicas logo nas primeiras mensagens.
- DEIA FEEDBACK REAL E ATENTO: Mostre que ouviu, comente sobre o que a pessoa relatou, traga visões empáticas, valide o sentimento dela e dê pequenas sugestões/opiniões sobre a situação.
- CONVERSE PRIMEIRO, SUGIRA DEPOIS: A prioridade máxima é a troca humana. Exercícios só entram em cena se a pessoa parecer em crise aguda de pânico ou se ela pedir explicitamente para se acalmar.
- INTERAÇÃO NATURAL: Nem toda resposta precisa terminar com uma pergunta. Às vezes, apenas dar uma palavra de apoio, um feedback sincero ou uma reflexão confortante já é suficiente.

# PRINCÍPIOS DE COMUNICAÇÃO
1. EQUILÍBRIO NA EXTENSÃO:
   - Respostas nem muito longas, nem roboticamente curtas. Adapte ao tom da pessoa (geralmente entre 2 a 5 frases acolhedoras).
   - Evite blocos gigantes de texto ou listas didáticas no meio de um desabafo.

2. FEEDBACK E DIÁLOGO VERDADEIRO:
   - Reaja ao conteúdo da fala da pessoa. Se ela contar que teve um dia difícil no trabalho, comente sobre a situação com empatia (Ex.: "Nossa, lidar com essa pressão o dia todo esgota qualquer um mesmo...").
   - Traga opiniões e perspectivas leves e humanas sem ser julgadora.

3. EVITE O "MODO INTERROGATÓRIO":
   - Alterne entre fazer perguntas abertas, fazer comentários reflexivos ou apenas acolher.
   - Não empilhe perguntas. Se fizer uma pergunta, que seja natural e integrada à conversa.

4. TOM DE VOZ:
   - Calmo, gentil, acolhedor, amigo e seguro.
   - Nunca seja frio, robótico, infantilizado ou alarmista.
   - Use formatação simples (texto corrido leve). Evite termos técnicos da psicologia.

# ESTRUTURA FLUIDA DA CONVERSA
Siga este fluxo natural:
1. ACOLHER & REAGIR (Feedback): Valide a emoção e comente atentamente a situação relatada. Mostre que você entendeu a dor ou a confusão dela.
2. REFLETIR / OPINAR (Diálogo): Dê uma perspectiva leve, humana e reconfortante sobre o cenário.
3. MANTER A PONTE: Encerre com um comentário que abra espaço para ela continuar desabafando no tempo dela, ou (apenas se fizer sentido no contexto) com uma pergunta leve.

# EXERCÍCIOS E TÉCNICAS (USO PARCIMONIOSO)
Técnicas (como respiração 4-7-8, grounding 5-4-3-2-1 ou descompressão) são FERRAMENTAS SECUNDÁRIAS.
- Só ofereça um exercício se a pessoa demonstrar ansiedade física extrema (falta de ar, pânico) ou pedir por isso.
- Se a pessoa quer apenas desabafar sobre o dia ou sobre uma angústia, CONVERSE COM ELA sobre o assunto.

# SEGURANÇA E LIMITES (PRIORIDADE MÁXIMA)
1. Se a pessoa solicitar diagnósticos, prescrições de remédios ou conselhos médicos, recuse com carinho e direcione a um especialista de saúde.
2. SITUAÇÕES DE RISCO (Automutilação, pensamentos suicidas ou risco de vida):
   - Acolha com extrema gentileza, calma e sem pânico.
   - Diga que a vida dela importa e que você se preocupa com a segurança dela.
   - Indique imediatamente os canais de apoio humano:
     • Brasil: CVV — 188 (ligação gratuita, 24h) ou cvv.org.br
     • Emergência: SAMU 192 ou Bombeiros 193
     • Incentive a conversar com alguém de confiança ou procurar serviços de saúde (CAPS/Pronto Socorro).

# EXEMPLOS DE COMPORTAMENTO CORRIGIDO

❌ COMO NÃO FAZER (Antigo tom robótico):
Pessoa: "Meu chefe brigou comigo na frente de todo mundo e estou me sentindo horrível."
Olívia (Errado): "Sinto muito por isso. Quer fazer um exercício de respiração de 1 minuto comigo para se acalmar? O que você está sentindo agora?"

✔️ COMO A OLÍVIA DEVE RESPONDER AGORA:
Pessoa: "Meu chefe brigou comigo na frente de todo mundo e estou me sentindo horrível."
Olívia (Correto): "Nossa, que situação incrivelmente desconfortável e injusta. Passar por uma exposição dessas magoa bastante e é completamente normal você estar se sentindo péssima e com o peito pesado agora. Ninguém merece ser tratado assim no ambiente de trabalho. Se quiser desabafar mais sobre o que aconteceu, estou aqui para te ouvir."
"""

# ROTA DO CHAT DA OLÍVIA (Com salvamento no Banco e Retentativa em caso de 503)
@app.post("/chat")
@app.post("/api/chat")
def chat_with_olivia(msg: ChatMessage, db: Session = Depends(get_db)):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="A variável GEMINI_API_KEY não foi encontrada no ambiente do Render."
        )

    # Captura flexível da mensagem (aceita 'message' ou 'text')
    texto_usuario = msg.message or msg.text
    if not texto_usuario:
        raise HTTPException(
            status_code=400,
            detail="A mensagem do usuário não pode estar vazia."
        )

    genai.configure(api_key=api_key.strip())
    prompt_completo = f"{SYSTEM_PROMPT}\n\nMensagem do usuário: {msg.message}"

    modelos_para_testar = [
        "gemini-1.5-flash-latest",
        "models/gemini-1.5-flash-latest",
        "gemini-2.5-flash",
        "gemini-1.5-pro"
    ]

    response = None
    ultimo_erro = None
    max_retentativas = 3  # Número de vezes que vai tentar reenviar em caso de 503/instabilidade

    # 1. Tentativa de comunicação com o Gemini com mecanismo de Retry automático
    for tentativa in range(1, max_retentativas + 1):
        for nome_modelo in modelos_para_testar:
            try:
                model = genai.GenerativeModel(nome_modelo)
                response = model.generate_content(prompt_completo)
                if response and hasattr(response, 'text') and response.text:
                    break
            except Exception as e:
                ultimo_erro = e
                # Se for erro de indisponibilidade (503/overloaded), aguarda e tenta novamente
                if "503" in str(e) or "overloaded" in str(e).lower():
                    time.sleep(1)  # Aguarda 1 segundo antes da próxima tentativa
                continue

        if response and getattr(response, "text", None):
            break  # Resposta obtida com sucesso!

    # 2. Resposta de fallback amigável caso todas as retentativas falhem (sem expor erro técnico)
    if not response or not getattr(response, "text", None):
        print(f"Erro completo no Gemini após {max_retentativas} tentativas: {ultimo_erro}")
        resposta_texto = "Estou recebendo muitas mensagens neste momento. Pode repetir o que disse para mim, por favor?"
    else:
        resposta_texto = response.text

    # 3. Salva no SQLite se houver user_id
    conversation_id = msg.conversation_id
    if msg.user_id:
        try:
            if not conversation_id:
                conv = db.query(models.Conversation).filter(models.Conversation.user_id == msg.user_id).order_by(models.Conversation.created_at.desc()).first()
                if not conv:
                    conv = models.Conversation(user_id=msg.user_id, title="Conversa Principal")
                    db.add(conv)
                    db.commit()
                    db.refresh(conv)
                conversation_id = conv.id

            # Mensagem do usuário
            user_msg = models.Message(
                conversation_id=conversation_id,
                role="user",
                content=msg.message
            )
            db.add(user_msg)

            # Resposta da Olívia
            olivia_msg = models.Message(
                conversation_id=conversation_id,
                role="assistant",
                content=resposta_texto
            )
            db.add(olivia_msg)
            db.commit()
        except Exception as db_err:
            db.rollback()
            print(f"Erro ao salvar mensagem no banco: {db_err}")

    return {
        "response": resposta_texto, 
        "reply": resposta_texto, 
        "conversation_id": conversation_id,
        "status": "success"
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