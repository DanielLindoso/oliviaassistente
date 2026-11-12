# 💜 Olívia Assistente - Apoio Emocional & Bem-Estar

> **Projeto Integrador - SENAI**  
> **Equipe de desenvolvimento:** Daniel Lindoso, Josiane, Matheus, Michael  
> **Stack:** Python (FastAPI), HTML5/CSS3/JavaScript (SPA), SQLite/SQLAlchemy, Google Gemini AI API  
> **Deploy:** Render (Backend API) & Vercel (Frontend SPA)

---

## 📌 Sobre a Olívia
A **Olívia** é uma assistente virtual focada no acompanhamento emocional e apoio prático para momentos de ansiedade, estresse e sobrecarga diária. O objetivo do projeto é oferecer um espaço seguro, empático e acessível, combinando a capacidade de escuta ativa de Modelos de Linguagem Generativa (LLM) com ferramentas práticas de autorregulação emocional.

---

## 🚀 Arquitetura e Tecnologias

A aplicação adota uma arquitetura descentralizada (*Decoupled Client-Server*), separando completamente a interface de usuário da API de negócios.

### Backend (API RESTful)
- **Python 3.10+** & **FastAPI**: Framework assíncrono de alta performance.
- **Google Generative AI SDK (`gemini-1.5-flash`)**: Processamento de linguagem natural configurado com engenharia de prompt voltada para escuta empática.
- **SQLAlchemy & SQLite**: ORM para persistência de dados de usuários e histórico de diálogos.
- **Bcrypt**: Criptografia e segurança de senhas de usuários.
- **Uvicorn**: Servidor ASGI utilizado na produção.

### Frontend (SPA Web)
- **Single Page Application (SPA)**: Desenvolvida com HTML5 semântico, CSS3 e JavaScript Moderno (ES6+), sem dependências pesadas de frameworks externos.
- **UI/UX Acolhedora**: Interface responsiva desenvolvida com paleta em tons de lilás e roxo, focada na indução visual de calma e simplicidade de uso.

---

## 🛠️ Principais Recursos

1. **Chat de Escuta Empática:** Interação em tempo real com a Olívia, adaptada para conversas não invasivas e acolhedoras.
2. **Atividades Práticas de Regulação Emocional:** 
   - *Exercício de Respiração Diafragmática (5 min)* para redução de ansiedade.
   - *Diário da Gratidão* para ancoragem de pensamentos positivos.
3. **Histórico de Conversas:** Consulta às sessões e mensagens passadas gravadas na base de dados.
4. **Dashboard de Progresso:** Monitoramento motivacional de conversas e atividades concluídas.
5. **Perfil & Personalização:** Gerenciamento de dados da conta e alternância entre Modo Claro e Modo Escuro.

---

## 📁 Estrutura do Repositório

```text
oliviaassistente/
├── frontend/                 # Interface Web (Single Page Application)
│   ├── css/                  # Estilos visuais (style.css, home.css)
│   ├── images/               # Imagens e avatares do sistema
│   ├── js/                   # Scripts e integração com API (app.js)
│   ├── chat.html             # Estrutura das telas internas
│   └── index.html            # Landing page / Tela inicial
├── oliviaassistente/         # Backend (API Python FastAPI)
│   ├── auth.py               # Módulo de autenticação e segurança
│   ├── database.py           # Conexão e sessão da base de dados SQLite
│   ├── main.py               # Rotas REST e integração com Gemini AI
│   └── models.py             # Modelos de tabelas SQLAlchemy
├── .gitignore                # Arquivos ignorados pelo Git
├── README.md                 # Documentação oficial do projeto
└── requirements.txt          # Dependências do backend Python
🔧 Como Executar o Projeto LocalmentePré-requisitosPython 3.10+ instaladoGit instaladoUma chave de API ativa da Google Gemini API (GEMINI_API_KEY)1. Clonar o RepositórioBashgit clone [https://github.com/DanielLindoso/oliviaassistente.git](https://github.com/DanielLindoso/oliviaassistente.git)
cd oliviaassistente
2. Criar e Ativar o Ambiente VirtualBash# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
3. Instalar as DependênciasBashpip install -r requirements.txt
4. Configurar Variáveis de AmbienteCrie um arquivo .env na pasta raiz ou configure no ambiente:Snippet de códigoGEMINI_API_KEY=sua_chave_do_gemini_aqui
5. Iniciar o BackendBashcd oliviaassistente
uvicorn main:app --reload
A API estará acessível em http://127.0.0.1:8000.6. Iniciar o FrontendAbra o arquivo frontend/index.html em qualquer navegador web ou utilize a extensão Live Server do Visual Studio Code.📑 Rotas Principais da APIMétodoRotaDescriçãoGET/Endpoint de verificação de status da APIPOST/api/chatEnvio de mensagens e geração de resposta empáticaGET/api/chat/history/{user_id}Recuperação do histórico de mensagens do usuário🎯 Visão de Futuro & Roadmap[ ] Implementação de RAG (Retrieval-Augmented Generation) utilizando LangChain e ChromaDB para embasamento de respostas em manuais de Psicoterapia Cognitivo-Comportamental (TCC).[ ] Suporte a áudios guiados para os exercícios de respiração e relaxamento.