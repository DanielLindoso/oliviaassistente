# Olivia 💙

A Olivia é uma inteligência artificial desenvolvida para oferecer apoio e conversas acolhedoras em momentos de ansiedade.

O projeto tem como objetivo disponibilizar um espaço acessível onde o usuário possa conversar, expressar o que está sentindo e receber respostas da inteligência artificial de acordo com o contexto da conversa.

> A Olivia é um protótipo de apoio e conversa. Ela não realiza diagnóstico, tratamento psicológico ou substitui profissionais de saúde.

---

## 🎯 Problema

Pessoas que passam por momentos de ansiedade podem sentir necessidade de conversar e expressar o que estão sentindo, mas nem sempre encontram um espaço acessível e imediato para isso.

A Olivia busca oferecer uma alternativa de conversa e apoio por meio de inteligência artificial.

---

## 💡 Solução

A Olivia permite que o usuário:

- acesse a aplicação pela web;
- inicie uma conversa;
- envie mensagens descrevendo o que está sentindo;
- receba respostas geradas por inteligência artificial;
- continue a conversa de maneira natural.

---

## 👤 Usuário

O sistema é destinado a pessoas que estejam passando por momentos de ansiedade e desejem utilizar um espaço de conversa e apoio.

---

## 🚀 Jornada principal do MVP

A jornada principal escolhida para o MVP é:

1. O usuário acessa a Olivia.
2. O usuário seleciona a opção para conversar.
3. O usuário envia uma mensagem.
4. A Olivia processa a mensagem utilizando inteligência artificial.
5. A Olivia apresenta uma resposta ao usuário.
6. O usuário pode continuar a conversa.

---

## 📋 Backlog do MVP

| # | Tarefa |
|---|---|
| 1 | Criar uma página inicial apresentando a proposta da Olivia |
| 2 | Disponibilizar o acesso à tela de conversa |
| 3 | Permitir o envio de mensagens pelo usuário |
| 4 | Integrar a aplicação com a API de inteligência artificial |
| 5 | Exibir a resposta da Olivia na conversa |

---

## ✅ Critérios de aceite

### CA1 — Envio de mensagem

O usuário consegue enviar uma mensagem pelo chat.

### CA2 — Processamento pelo backend

A mensagem chega ao backend e é processada pela Olivia.

### CA3 — Exibição da resposta

A resposta da Olivia aparece corretamente na interface.

### CA4 — Tratamento de erro

O sistema apresenta uma mensagem amigável quando ocorre um erro.

---

## 🛑 Limites do MVP

O MVP não contempla:

- diagnóstico psicológico;
- tratamento clínico;
- substituição de psicólogos ou outros profissionais;
- acompanhamento terapêutico;
- avaliação médica;
- funcionalidades avançadas de histórico ou personalização.

O objetivo desta versão é demonstrar a jornada principal de conversa e apoio por inteligência artificial.

---

## 🛠️ Tecnologias

### Frontend

- HTML
- CSS
- JavaScript

### Backend

- Python
- FastAPI
- Uvicorn

### Inteligência Artificial

- Google Gemini API

### Deploy

- Vercel — frontend
- Render — backend/API

### Versionamento

- Git
- GitHub

---

## 📁 Estrutura do projeto

```text
oliviaassistente/
│
├── frontend/
│   ├── index.html
│   ├── chat.html
│   ├── css/
│   │   ├── home.css
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── oliviaassistente/
│   ├── app/
│   │   └── main.py
│   │
│   ├── core/
│   │   ├── ia.py
│   │   ├── olivia_service.py
│   │   └── tarefas.py
│   │
│   ├── data/
│   │   └── data_manager.py
│   │
│   ├── ui/
│   │   ├── menus.py
│   │   └── utils.py
│   │
│   └── requirements.txt
│
├── README.md
├── IA_LOG.md
└── .gitignore