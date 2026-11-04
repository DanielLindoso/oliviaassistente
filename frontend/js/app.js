/* ==========================================================================
   LÓGICA SPA, AUTENTICAÇÃO E CHAT - OLIVIA ASSISTENTE
   ========================================================================== */

const API_BASE_URL = "https://olivia-fskx.onrender.com";

document.addEventListener("DOMContentLoaded", () => {
  checkSession();

  // Escuta tecla Enter no input do chat
  document.getElementById("chat-input-field")?.addEventListener("keypress", (e) => {
    if (e.key === "Enter") handleSendMessage();
  });
});

// Alterna entre páginas externas da SPA (Home, Login, Cadastro)
function navigateTo(screenId) {
  document.querySelectorAll(".view-screen").forEach(el => {
    el.classList.remove("active");
    el.style.display = "none";
  });
  
  document.getElementById("app-dashboard-wrapper").style.display = "none";

  const target = document.getElementById(screenId);
  if (target) {
    target.style.display = "flex";
    setTimeout(() => target.classList.add("active"), 10);
  }
}

// Alterna entre as abas da Sidebar interna
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
}

// Checa estado da sessão salva no localStorage
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

    document.getElementById("chat-user-greeting").innerText = `Olá, ${userName || ''}!`;
    document.getElementById("profile-name").innerText = userName || 'Usuário';
    document.getElementById("profile-email").innerText = localStorage.getItem("user_email") || '-';

    switchDashboardTab("screen-chat");
    fetchHistory();
  } else {
    navigateTo("screen-home");
  }
}

// Login SPA
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

// Cadastro SPA
async function handleCadastro(e) {
  if (e) e.preventDefault();

  const alertBox = document.getElementById("cadastro-alert");
  if (alertBox) alertBox.style.display = "none";

  const name = document.getElementById("reg-name")?.value.trim();
  const email = document.getElementById("reg-email")?.value.trim();
  const password = document.getElementById("reg-password")?.value.trim();

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
      alert("Cadastro concluído com sucesso! Faça login para acessar.");
      navigateTo("screen-login");
    } else {
      if (alertBox) {
        alertBox.innerText = data.detail || "Erro no cadastro.";
        alertBox.style.display = "block";
      }
    }
  } catch (err) {
    if (alertBox) {
      alertBox.innerText = "Erro de conexão com o servidor.";
      alertBox.style.display = "block";
    }
  }
}

// Envio de Mensagens no Chat
async function handleSendMessage() {
  const input = document.getElementById("chat-input-field");
  const messageText = input.value.trim();
  if (!messageText) return;

  const container = document.getElementById("chat-messages-container");

  // Balão de mensagem do usuário
  const userBubble = document.createElement("div");
  userBubble.className = "message-bubble user";
  userBubble.innerText = messageText;
  container.appendChild(userBubble);

  input.value = "";
  container.scrollTop = container.scrollHeight;

  const userId = localStorage.getItem("user_id");

  try {
    const res = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: messageText,
        user_id: userId ? parseInt(userId) : null
      })
    });

    const data = await res.json();

    // Balão de resposta da Olívia
    const oliviaBubble = document.createElement("div");
    oliviaBubble.className = "message-bubble olivia";
    oliviaBubble.innerText = data.response || data.reply || "Desculpe, tive uma instabilidade.";
    container.appendChild(oliviaBubble);
    container.scrollTop = container.scrollHeight;

  } catch (err) {
    const errorBubble = document.createElement("div");
    errorBubble.className = "message-bubble olivia";
    errorBubble.innerText = "Estou recebendo muitas mensagens. Pode tentar novamente em instantes?";
    container.appendChild(errorBubble);
  }
}

// Busca Histórico de Mensagens do SQLite
async function fetchHistory() {
  const userId = localStorage.getItem("user_id");
  if (!userId) return;

  const listContainer = document.getElementById("history-list-container");

  try {
    const res = await fetch(`${API_BASE_URL}/api/chat/history/${userId}`);
    const data = await res.json();

    if (res.ok && data.messages && data.messages.length > 0) {
      listContainer.innerHTML = "";
      data.messages.forEach(msg => {
        const item = document.createElement("div");
        item.style.cssText = "background: var(--white); padding: 20px; border-radius: var(--radius-md); margin-bottom: 14px; box-shadow: var(--shadow-subtle); border: 1px solid #F0EBFA;";
        item.innerHTML = `<strong style="color: var(--purple-dark);">${msg.role === 'user' ? 'Você' : 'Olivia'}:</strong> <p style="margin-top: 6px; color: var(--text-muted); font-size: 0.95rem;">${msg.content}</p>`;
        listContainer.appendChild(item);
      });
    } else {
      listContainer.innerHTML = "<p style='color: var(--text-muted);'>Nenhuma conversa registrada ainda.</p>";
    }
  } catch (err) {
    listContainer.innerHTML = "<p style='color: var(--danger);'>Erro ao carregar histórico de conversas.</p>";
  }
}

// Modal de Logout
function showLogoutModal() {
  document.getElementById("logout-modal").classList.add("active");
}

function confirmLogout() {
  localStorage.clear();
  document.getElementById("logout-modal").classList.remove("active");
  navigateTo("screen-home");
}

/* ==========================================================================
   ATIVIDADES INTERATIVAS (SEM JANELAS DE ALERT)
   ========================================================================== */

let breathingTimer = null;

// 1. Exercício Guiado de Respiração Animado
function startBreathingExercise() {
  const modal = document.getElementById("activity-modal");
  const body = document.getElementById("activity-modal-body");

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
      // Inspire (4s)
      circle.className = "breathing-circle expand";
      circle.innerText = "Inspire";
      instruction.innerText = "Inspire lentamente pelo nariz... (4s)";
      phase = 1;
      breathingTimer = setTimeout(cycle, 4000);
    } else if (phase === 1) {
      // Segure (4s)
      circle.className = "breathing-circle hold";
      circle.innerText = "Segure";
      instruction.innerText = "Mantenha o ar nos pulmões... (4s)";
      phase = 2;
      breathingTimer = setTimeout(cycle, 4000);
    } else {
      // Expire (6s)
      circle.className = "breathing-circle shrink";
      circle.innerText = "Expire";
      instruction.innerText = "Solte o ar bem devagar pela boca... (6s)";
      phase = 0;
      breathingTimer = setTimeout(cycle, 6000);
    }
  }

  // Inicia após 1.5s
  breathingTimer = setTimeout(cycle, 1500);
}

// 2. Diário da Gratidão Interativo
function startGratitudeExercise() {
  const modal = document.getElementById("activity-modal");
  const body = document.getElementById("activity-modal-body");

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

  if (!i1 && !i2 && !i3) {
    alert("Escreva pelo menos 1 motivo de gratidão antes de registrar.");
    return;
  }

  incrementActivityCount();

  const body = document.getElementById("activity-modal-body");
  body.innerHTML = `
    <div class="modal-icon"><i class="fa-solid fa-check"></i></div>
    <h3 style="color: var(--purple-dark); font-size: 1.4rem;">Registro Concluído!</h3>
    <p style="color: var(--text-muted); margin: 12px 0 24px 0;">Parabéns por tirar esse tempo para você hoje! <i class="fa-solid fa-heart" style="color: var(--purple-main);"></i></p>
    <button class="btn-primary" onclick="closeActivityModal()">Fechar</button>
  `;
}
// Fechar Modal de Atividades
function closeActivityModal() {
  const modal = document.getElementById("activity-modal");
  modal.classList.remove("active");
  if (breathingTimer) clearTimeout(breathingTimer);
  incrementActivityCount();
}

// Função para atualizar os dados do Dashboard de Progresso
async function updateProgressDashboard() {
  const userId = localStorage.getItem("user_id");
  
  // 1. Contador de Atividades (salvo localmente)
  const activitiesCompleted = localStorage.getItem(`activities_completed_${userId}`) || "0";
  const activitiesElem = document.getElementById("stat-atividades-count");
  if (activitiesElem) activitiesElem.innerText = activitiesCompleted;

  // 2. Contador de Mensagens no Chat (buscado do SQLite)
  if (userId) {
    try {
      const res = await fetch(`${API_BASE_URL}/api/chat/history/${userId}`);
      const data = await res.json();
      const countElem = document.getElementById("stat-conversas-count");
      
      if (res.ok && data.messages && countElem) {
        countElem.innerText = data.messages.length;
      }
    } catch (err) {
      console.error("Erro ao atualizar estatísticas de conversas:", err);
    }
  }
}

// Atualizar a troca de abas para recarregar o progresso quando clicar na aba "Progresso"
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

// Incrementar contador de atividades quando o usuário conclui o exercício de respiração ou gratidão
function incrementActivityCount() {
  const userId = localStorage.getItem("user_id");
  if (!userId) return;
  
  let current = parseInt(localStorage.getItem(`activities_completed_${userId}`) || "0");
  current += 1;
  localStorage.setItem(`activities_completed_${userId}`, current.toString());
  
  updateProgressDashboard();
}