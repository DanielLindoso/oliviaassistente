/* ==========================================================================
   LÓGICA SPA, AUTENTICAÇÃO, CHAT E HISTÓRICO - OLIVIA ASSISTENTE
   ========================================================================== */

const API_BASE_URL = "https://olivia-fskx.onrender.com";

document.addEventListener("DOMContentLoaded", () => {
  checkSession();

  // Escuta a tecla Enter no campo de input do chat
  document.getElementById("chat-input-field")?.addEventListener("keypress", (e) => {
    if (e.key === "Enter") handleSendMessage();
  });
});

// Alterna entre as telas da SPA (Home, Login, Cadastro)
function navigateTo(screenId) {
  document.querySelectorAll(".view-screen").forEach(el => {
    el.classList.remove("active");
    el.style.display = "none";
  });
  
  const appWrapper = document.getElementById("app-dashboard-wrapper");
  if (appWrapper) appWrapper.style.display = "none";

  const target = document.getElementById(screenId);
  if (target) {
    target.style.display = "flex";
    setTimeout(() => target.classList.add("active"), 10);
  }
}

// Iniciar uma Nova Conversa
function startNewConversation() {
  const container = document.getElementById("chat-messages-container");
  if (container) {
    container.innerHTML = `
      <div class="message-bubble olivia">
        Olá! Nova conversa iniciada. Como posso te apoiar agora?
      </div>
    `;
  }
  
  switchDashboardTab("screen-chat");
  document.getElementById("chat-input-field")?.focus();
}

// Alterna entre as abas internas da Sidebar (Chat, Atividades, Histórico, Progresso, Perfil, Configurações)
function switchDashboardTab(tabId) {
  document.querySelectorAll(".dashboard-tab").forEach(el => el.style.display = "none");
  document.querySelectorAll(".sidebar-menu li").forEach(el => el.classList.remove("active"));

  const targetTab = document.getElementById(tabId);
  if (targetTab) targetTab.style.display = "block";

  const menuMap = {
    'screen-chat': 'menu-chat',
    'screen-atividades': 'menu-atividades',
    'screen-historico': 'menu-historico',
    'screen-progresso': 'menu-progresso',
    'screen-perfil': 'menu-perfil',
    'screen-config': 'menu-config'
  };

  if (menuMap[tabId]) {
    document.getElementById(menuMap[tabId])?.classList.add("active");
  }

  if (tabId === 'screen-historico') fetchHistory();
  if (tabId === 'screen-progresso') updateProgressDashboard();
}

// Verifica estado da sessão ativa no localStorage
function checkSession() {
  const userId = localStorage.getItem("user_id");
  const userName = localStorage.getItem("user_name");

  if (userId) {
    document.querySelectorAll(".view-screen").forEach(el => {
      el.classList.remove("active");
      el.style.display = "none";
    });

    const appWrapper = document.getElementById("app-dashboard-wrapper");
    if (appWrapper) appWrapper.style.display = "flex";

    const greeting = document.getElementById("chat-user-greeting");
    if (greeting) greeting.innerText = `Olá, ${userName || ''}!`;

    const profileName = document.getElementById("profile-name");
    if (profileName) profileName.innerText = userName || 'Usuário';

    const profileEmail = document.getElementById("profile-email");
    if (profileEmail) profileEmail.innerText = localStorage.getItem("user_email") || '-';

    switchDashboardTab("screen-chat");
    fetchHistory();
    updateProgressDashboard();
  } else {
    navigateTo("screen-home");
  }
}

// Handler do Login
async function handleLogin(e) {
  if (e) e.preventDefault();

  const alertBox = document.getElementById("login-alert");
  if (alertBox) alertBox.style.display = "none";

  const email = document.getElementById("login-email")?.value.trim();
  const password = document.getElementById("login-password")?.value.trim();

  if (!email || !password) return;

  try {
    let res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    if (!res.ok) {
      res = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
    }

    const data = await res.json();

    if (res.ok) {
      localStorage.setItem("user_id", data.user_id);
      localStorage.setItem("user_name", data.name || "Usuário");
      localStorage.setItem("user_email", data.email || email);
      checkSession();
    } else {
      if (alertBox) {
        alertBox.innerText = data.detail || "E-mail ou senha incorretos.";
        alertBox.style.display = "block";
      }
    }
  } catch (err) {
    if (alertBox) {
      alertBox.innerText = "Erro ao conectar com o servidor da Olívia.";
      alertBox.style.display = "block";
    }
  }
}

// Handler do Cadastro com feedback interno
async function handleCadastro(e) {
  if (e) e.preventDefault();

  const alertBox = document.getElementById("cadastro-alert");
  if (alertBox) {
    alertBox.style.display = "none";
    alertBox.className = "alert-box alert-danger";
  }

  const name = document.getElementById("reg-name")?.value.trim();
  const email = document.getElementById("reg-email")?.value.trim();
  const password = document.getElementById("reg-password")?.value.trim();

  if (!name || !email || !password) return;

  try {
    let res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password })
    });

    if (!res.ok) {
      res = await fetch(`${API_BASE_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password })
      });
    }

    const data = await res.json();

    if (res.ok) {
      const loginAlert = document.getElementById("login-alert");
      if (loginAlert) {
        loginAlert.innerText = "Cadastro realizado com sucesso! Faça login para continuar.";
        loginAlert.className = "alert-box alert-success";
        loginAlert.style.display = "block";
      }

      document.getElementById("cadastro-form")?.reset();
      navigateTo("screen-login");
    } else {
      if (alertBox) {
        alertBox.innerText = data.detail || "Erro ao realizar o cadastro.";
        alertBox.className = "alert-box alert-danger";
        alertBox.style.display = "block";
      }
    }
  } catch (err) {
    if (alertBox) {
      alertBox.innerText = "Erro de conexão com o servidor.";
      alertBox.className = "alert-box alert-danger";
      alertBox.style.display = "block";
    }
  }
}

// Envio de mensagem com salvamento local no Histórico
async function handleSendMessage() {
  const input = document.getElementById("chat-input-field");
  const messageText = input.value.trim();
  if (!messageText) return;

  const container = document.getElementById("chat-messages-container");

  // Adiciona a bolha do usuário
  const userBubble = document.createElement("div");
  userBubble.className = "message-bubble user";
  userBubble.innerText = messageText;
  container.appendChild(userBubble);

  input.value = "";
  container.scrollTop = container.scrollHeight;

  const rawUserId = localStorage.getItem("user_id");
  const userId = rawUserId ? parseInt(rawUserId, 10) : null;

  // Salva a mensagem no histórico local instantaneamente
  saveMessageToLocalHistory(rawUserId, 'user', messageText);

  try {
    const res = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: messageText,
        user_id: userId
      })
    });

    const data = await res.json();
    const botResponse = data.response || data.reply || "Desculpe, tive uma instabilidade.";

    // Adiciona a bolha da Olívia
    const oliviaBubble = document.createElement("div");
    oliviaBubble.className = "message-bubble olivia";
    oliviaBubble.innerText = botResponse;
    container.appendChild(oliviaBubble);
    container.scrollTop = container.scrollHeight;

    // Salva a resposta da Olívia no histórico local
    saveMessageToLocalHistory(rawUserId, 'assistant', botResponse);

    updateProgressDashboard();

  } catch (err) {
    const errorBubble = document.createElement("div");
    errorBubble.className = "message-bubble olivia";
    errorBubble.innerText = "Estou recebendo muitas mensagens. Pode tentar novamente em instantes?";
    container.appendChild(errorBubble);
  }
}

// Função auxiliar para armazenar o histórico localmente
function saveMessageToLocalHistory(userId, role, content) {
  const key = `chat_history_${userId || 'guest'}`;
  let history = [];
  try {
    history = JSON.parse(localStorage.getItem(key)) || [];
  } catch (e) {
    history = [];
  }
  history.push({ role, content, created_at: new Date().toISOString() });
  localStorage.setItem(key, JSON.stringify(history));
}

// Busca e exibe o histórico de conversas (Backend + LocalStorage Fallback)
async function fetchHistory() {
  const rawUserId = localStorage.getItem("user_id");
  const listContainer = document.getElementById("history-list-container");
  if (!listContainer) return;

  listContainer.innerHTML = "<p style='color: var(--text-muted);'>Carregando histórico...</p>";

  let messages = [];

  // 1. Tenta buscar o histórico real do SQLite via API
  if (rawUserId) {
    const userId = parseInt(rawUserId, 10);
    try {
      const res = await fetch(`${API_BASE_URL}/api/chat/history/${userId}`);
      if (res.ok) {
        const data = await res.json();
        // O backend FastAPI retorna a chave "history" ou "messages"
        messages = data.history || data.messages || [];
      }
    } catch (err) {
      console.warn("Erro ao buscar histórico da API, verificando cache local...", err);
    }
  }

  // 2. Se a API não retornar mensagens, carrega as conversas salvas no LocalStorage local
  if (messages.length === 0) {
    const localHistory = localStorage.getItem(`chat_history_${rawUserId || 'guest'}`);
    if (localHistory) {
      try {
        messages = JSON.parse(localHistory);
      } catch (e) {
        messages = [];
      }
    }
  }

  // 3. Renderização das mensagens no painel
  if (messages.length > 0) {
    listContainer.innerHTML = "";
    messages.forEach((item, index) => {
      const div = document.createElement("div");
      div.style.cssText = "background: var(--white); padding: 20px; border-radius: var(--radius-md); margin-bottom: 14px; box-shadow: var(--shadow-subtle); border: 1px solid #F0EBFA; transition: var(--transition-fast); cursor: pointer;";

      const role = item.role || item.sender || 'assistant';
      const isUser = (role === 'user');
      const author = isUser ? 'Você' : 'Olivia';
      const content = item.content || item.message || item.text || 'Mensagem sem texto';
      const date = item.created_at ? new Date(item.created_at).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '';

      div.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <strong style="color: var(--purple-dark); font-size: 1rem;">${author}</strong>
          <span style="font-size: 0.8rem; color: var(--text-muted);">${date}</span>
        </div>
        <p style="color: var(--text-muted); font-size: 0.92rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${content}</p>
      `;

      // Permite reabrir a conversa no chat ao clicar no item
      div.addEventListener("click", () => {
        const container = document.getElementById("chat-messages-container");
        if (container) {
          container.innerHTML = `
            <div class="message-bubble ${isUser ? 'user' : 'olivia'}">${content}</div>
          `;
        }
        switchDashboardTab("screen-chat");
      });

      listContainer.appendChild(div);
    });
  } else {
    listContainer.innerHTML = "<p style='color: var(--text-muted);'>Nenhuma conversa registrada ainda no histórico.</p>";
  }
}

// Atualiza o painel de progresso
async function updateProgressDashboard() {
  const rawUserId = localStorage.getItem("user_id");
  if (!rawUserId) return;
  const userId = parseInt(rawUserId, 10);

  const activitiesCompleted = localStorage.getItem(`activities_completed_${userId}`) || "0";
  const activitiesElem = document.getElementById("stat-atividades-count");
  if (activitiesElem) activitiesElem.innerText = activitiesCompleted;

  try {
    let res = await fetch(`${API_BASE_URL}/conversations?user_id=${userId}`);
    if (!res.ok) {
      res = await fetch(`${API_BASE_URL}/api/chat/history/${userId}`);
    }
    const data = await res.json();
    const historyItems = data.messages || data.conversations || (Array.isArray(data) ? data : []);
    const countElem = document.getElementById("stat-conversas-count");

    if (res.ok && countElem) {
      countElem.innerText = historyItems.length;
    }
  } catch (err) {
    console.error("Erro ao atualizar contadores do progresso:", err);
  }
}

// Incrementar atividades concluídas
function incrementActivityCount() {
  const rawUserId = localStorage.getItem("user_id");
  if (!rawUserId) return;

  let current = parseInt(localStorage.getItem(`activities_completed_${rawUserId}`) || "0", 10);
  current += 1;
  localStorage.setItem(`activities_completed_${rawUserId}`, current.toString());

  updateProgressDashboard();
}

// Modais de Atividade Guiada (Sem Janelas Nativas)
let breathingTimer = null;

function startBreathingExercise() {
  const modal = document.getElementById("activity-modal");
  const body = document.getElementById("activity-modal-body");

  if (!modal || !body) return;

  body.innerHTML = `
    <div class="logo-icon" style="margin: 0 auto 16px auto;"><i class="fa-solid fa-wind"></i></div>
    <h3 style="color: var(--purple-dark); font-size: 1.5rem;">Respiração Guiada</h3>
    <p style="color: var(--text-muted); font-size: 0.95rem; margin-top: 6px;">Siga o ritmo do círculo para acalmar a mente</p>

    <div class="breathing-circle-wrapper">
      <div id="b-circle" class="breathing-circle">Prepare-se</div>
    </div>

    <p id="b-instruction" style="font-weight: 600; color: var(--purple-main); font-size: 1.1rem; min-height: 30px;">
      Relaxe os ombros...
    </p>
  `;

  modal.classList.add("active");

  const circle = document.getElementById("b-circle");
  const instruction = document.getElementById("b-instruction");

  let phase = 0;

  function cycle() {
    if (!modal.classList.contains("active")) return;

    if (phase === 0) {
      circle.className = "breathing-circle expand";
      circle.innerText = "Inspire";
      instruction.innerText = "Inspire lentamente pelo nariz... (4s)";
      phase = 1;
      breathingTimer = setTimeout(cycle, 4000);
    } else if (phase === 1) {
      circle.className = "breathing-circle hold";
      circle.innerText = "Segure";
      instruction.innerText = "Mantenha o ar nos pulmões... (4s)";
      phase = 2;
      breathingTimer = setTimeout(cycle, 4000);
    } else {
      circle.className = "breathing-circle shrink";
      circle.innerText = "Expire";
      instruction.innerText = "Solte o ar bem devagar pela boca... (6s)";
      phase = 0;
      breathingTimer = setTimeout(cycle, 6000);
    }
  }

  breathingTimer = setTimeout(cycle, 1500);
}

function startGratitudeExercise() {
  const modal = document.getElementById("activity-modal");
  const body = document.getElementById("activity-modal-body");

  if (!modal || !body) return;

  body.innerHTML = `
    <div class="logo-icon" style="margin: 0 auto 16px auto;"><i class="fa-solid fa-heart"></i></div>
    <h3 style="color: var(--purple-dark); font-size: 1.4rem;">Diário da Gratidão</h3>
    <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 6px; margin-bottom: 20px;">Escreva 3 coisas boas do seu dia pelas quais é grato:</p>

    <div style="display: flex; flex-direction: column; gap: 12px; text-align: left;">
      <input type="text" class="input-field" placeholder="1. Sou grato(a) por..." id="g-input-1">
      <input type="text" class="input-field" placeholder="2. Sou grato(a) por..." id="g-input-2">
      <input type="text" class="input-field" placeholder="3. Sou grato(a) por..." id="g-input-3">
    </div>

    <button class="btn-primary" style="width: 100%; margin-top: 24px;" onclick="saveGratitude()">Concluir e Salvar</button>
  `;

  modal.classList.add("active");
}

function saveGratitude() {
  const i1 = document.getElementById("g-input-1")?.value.trim();
  const i2 = document.getElementById("g-input-2")?.value.trim();
  const i3 = document.getElementById("g-input-3")?.value.trim();

  if (!i1 && !i2 && !i3) return;

  incrementActivityCount();

  const body = document.getElementById("activity-modal-body");
  if (body) {
    body.innerHTML = `
      <div class="modal-icon"><i class="fa-solid fa-check"></i></div>
      <h3 style="color: var(--purple-dark); font-size: 1.4rem;">Registro Concluído!</h3>
      <p style="color: var(--text-muted); margin: 12px 0 24px 0;">Parabéns por tirar esse tempo para você hoje! <i class="fa-solid fa-heart" style="color: var(--purple-main);"></i></p>
      <button class="btn-primary" onclick="closeActivityModal()">Fechar</button>
    `;
  }
}

function closeActivityModal() {
  const modal = document.getElementById("activity-modal");
  if (modal) modal.classList.remove("active");
  if (breathingTimer) clearTimeout(breathingTimer);
}

// Modal de Logout
function showLogoutModal() {
  const modal = document.getElementById("logout-modal");
  if (modal) modal.classList.add("active");
}

function confirmLogout() {
  localStorage.clear();
  const modal = document.getElementById("logout-modal");
  if (modal) modal.classList.remove("active");
  navigateTo("screen-home");
}