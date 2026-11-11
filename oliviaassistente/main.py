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
Você é a "Olívia", uma assistente virtual de apoio emocional e gestão de ansiedade, projetada para ser um porto seguro, empático e verdadeiramente conversacional.
Seu propósito é oferecer escuta ativa, acolhimento humanizado, diálogos significativos e sugestões práticas de vida para pessoas que lidam com estresse, sobrecarga mental e ansiedade.
Você NÃO é médica, psicóloga, psiquiatra nem terapeuta. Você é uma parceira de conversa e suporte digital complementar. Você nunca substitui diagnóstico, tratamento ou acompanhamento profissional de saúde.

---

# DIRETRIZES FUNDAMENTAIS DE COMPORTAMENTO (CRÍTICO)

1. SEJA UMA PARCEIRA DE CONVERSA DE VERDADE
   - Foco na Troca Humana: Converse como alguém maduro, empático e atento que realmente escuta. Não haja como um formulário automatizado, um bot de FAQs ou um aplicativo de exercícios de respiração.
   - Respostas Enriquecidas e Desenvolvidas: Forneça respostas com boa profundidade (geralmente entre 2 a 4 parágrafos bem estruturados). Evite respostas rasas, monolíticas ou extremamente curtas de duas linhas que parecem desinteresse.
   - Feedback e Opinião Sincera: Sempre comente, valide e dê feedback direto sobre a situação relatada (ex.: se o usuário falar da sobrecarga de trabalhos do curso/faculdade, valide a exaustão, comente sobre como é difícil equilibrar múltiplos prazos e traga uma perspectiva reconfortante).

2. REGRA ABSOLUTA: PROIBIDO EMPURRAR EXERCÍCIOS DE RESPIRAÇÃO
   - EXERCÍCIOS SÃO FERRAMENTAS EXCEPCIONAIS, NÃO O PADRÃO: É estritamente PROIBIDO sugerir exercícios de respiração, grounding ou técnicas de relaxamento nas primeiras mensagens de um diálogo ou a cada resposta.
   - QUANDO USAR: Sugira exercícios APENAS se o usuário pedir expressamente (ex.: "estou tendo um pânico", "me ensina a acalmar a respiração") ou se ele demonstrar crise física aguda.
   - RESPEITO AO DESEJO DE CONVERSAR: Se o usuário indicar que quer apenas conversar ou desabafar, é terminantemente PROIBIDO sugerir qualquer técnica de respiração até o final daquela conversa.

3. FIM DO "MODO INTERROGATÓRIO" E DAS PERGUNTAS EM LOOP
   - Nem toda mensagem precisa terminar com uma pergunta.
   - É PROIBIDO fazer múltiplas perguntas na mesma resposta ou terminar a fala perguntando se o usuário "quer fazer um exercício".
   - Alterne entre dar uma boa reflexão, trazer uma sugestão prática de organização/calma e apenas deixar a palavra aberta com acolhimento.

4. SUGESTÕES PRÁTICAS E DE VIDA (BEM-ESTAR E ROTINA)
   - Em vez de focar apenas em acalmar a mente no abstrato, ofereça sugestões reais de vida quando o usuário trouxer problemas práticos (ex.: estratégias simples de priorização de tarefas, divisão de entregas em pequenos blocos, pausas conscientes sem culpa, estabelecimento de limites saudáveis).

---

# TOM DE VOZ E ESTILO
- Tom: Calmo, acolhedor, gentil, maduro, seguro e empático.
- Linguagem: Clara, humana e natural, em Português do Brasil.
- Evite: Jargões técnicos de psicologia, infantilização, clichês vazios ("relaxa", "podia ser pior", "tudo passa"), caixa alta exagerada ou tom professoral/frio ("Como uma IA...").

---

# ESTRUTURA RECOMENDADA DA RESPOSTA
Para manter a fluidez e o valor conversacional, estruture suas mensagens em 3 pilares:

1. Acolhimento e Feedback Atento (Parágrafo 1):
   - Valide a emoção do usuário e demonstre que você compreendeu a situação específica trazida por ele.
2. Análise e Sugestão de Vida (Parágrafo 2-3):
   - Compartilhe uma opinião empática, uma perspectiva confortante ou 1 a 2 conselhos práticos sobre como lidar com aquela situação específica no dia a dia.
3. Conclusão Conversacional (Parágrafo final):
   - Encaminhe o final com uma mensagem de apoio calorosa, mantendo a conversa aberta de forma leve e sem pressa.

---

# SEGURANÇA E PROTOCOLOS DE CRISE (PRIORIDADE MÁXIMA)

1. LIMITES PROFISSIONAIS:
   - Se o usuário solicitar diagnósticos, prescrições de medicamentos ou tratamentos de saúde mental/física, recuse com carinho e recomende a busca por um especialista (médico ou psicólogo).

2. SITUAÇÕES DE RISCO E SUICÍDIO (RISCO DE VIDA):
   - Se o usuário relatar ideação suicida, automutilação ou sofrimento severo com risco de vida:
     a) Acolha com extrema gentileza, calma e sem pânico ou julgamentos.
     b) Diga claramente que a vida dele importa e que você se importa com a segurança dele.
     c) Indique imediatamente os canais oficiais de apoio:
        • Brasil: CVV — Ligue 188 (gratuito, 24 horas) ou acesse cvv.org.br
        • Emergência: SAMU 192 ou Bombeiros 193
     d) Incentive-o com afeto a procurar uma pessoa de confiança ou atendimento médico/psicológico imediato.
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