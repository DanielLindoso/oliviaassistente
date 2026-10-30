const API_BASE_URL = "https://olivia-fskx.onrender.com";

let currentUser = JSON.parse(localStorage.getItem("olivia_user")) || null;
let currentConversationId = localStorage.getItem("olivia_conversation_id") || null;
let tasks = JSON.parse(localStorage.getItem("olivia_tasks")) || [];

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    setupAuthListeners();
    setupChatListeners();
    setupTasksListeners();
    setupBreathingListeners();
    setupMoodListeners();
    checkAuthStatus();
});

// 1. CONTROLADOR DE SESSÃO E TELAS
function checkAuthStatus() {
    const authScreen = document.getElementById("auth-screen");
    const mainApp = document.getElementById("main-app");
    const userDisplay = document.getElementById("user-name-display");
    const userAvatar = document.getElementById("user-avatar");

    if (currentUser && currentUser.name) {
        if (authScreen) authScreen.classList.add("hidden");
        if (mainApp) mainApp.classList.remove("hidden");
        if (userDisplay) userDisplay.textContent = currentUser.name;
        if (userAvatar) userAvatar.textContent = currentUser.name.charAt(0).toUpperCase();
        renderTasks();
    } else {
        if (authScreen) authScreen.classList.remove("hidden");
        if (mainApp) mainApp.classList.add("hidden");
    }
}

function initNavigation() {
    const navButtons = document.querySelectorAll(".nav-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");

            navButtons.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.add("hidden"));

            btn.classList.add("active");
            const activeEl = document.getElementById(targetTab);
            if (activeEl) activeEl.classList.remove("hidden");
        });
    });
}

// 2. AUTENTICAÇÃO COM COMPATIBILIDADE DE ROTAS E MODO LOCAL
function setupAuthListeners() {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const showRegister = document.getElementById("show-register");
    const showLogin = document.getElementById("show-login");
    const logoutBtn = document.getElementById("logout-btn");

    if (showRegister) {
        showRegister.addEventListener("click", (e) => {
            e.preventDefault();
            loginForm.classList.add("hidden");
            registerForm.classList.remove("hidden");
        });
    }

    if (showLogin) {
        showLogin.addEventListener("click", (e) => {
            e.preventDefault();
            registerForm.classList.add("hidden");
            loginForm.classList.remove("hidden");
        });
    }

    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("reg-name").value;
            const email = document.getElementById("reg-email").value;
            const password = document.getElementById("reg-password").value;

            try {
                let response = await fetch(`${API_BASE_URL}/auth/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, email, password })
                });

                if (response.status === 404) {
                    response = await fetch(`${API_BASE_URL}/register`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ name, email, password })
                    });
                }

                const data = await response.json();
                if (response.ok) {
                    alert("Conta criada com sucesso! Faça login para continuar.");
                    registerForm.classList.add("hidden");
                    loginForm.classList.remove("hidden");
                } else {
                    alert(`Aviso: ${data.detail || 'Entrando no modo de testes...'}`);
                    loginUserLocally(name, email);
                }
            } catch (err) {
                loginUserLocally(name, email);
            }
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value;
            const password = document.getElementById("login-password").value;

            try {
                let response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password })
                });

                if (response.status === 404) {
                    response = await fetch(`${API_BASE_URL}/login`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ email, password })
                    });
                }

                const data = await response.json();
                if (response.ok) {
                    currentUser = data;
                    localStorage.setItem("olivia_user", JSON.stringify(data));
                    checkAuthStatus();
                } else {
                    loginUserLocally(email.split("@")[0], email);
                }
            } catch (err) {
                loginUserLocally(email.split("@")[0], email);
            }
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("olivia_user");
            localStorage.removeItem("olivia_conversation_id");
            currentUser = null;
            currentConversationId = null;
            checkAuthStatus();
        });
    }
}

function loginUserLocally(name, email) {
    currentUser = {
        name: name || "Usuário",
        email: email,
        user_id: 1,
        access_token: "local_session_token"
    };
    localStorage.setItem("olivia_user", JSON.stringify(currentUser));
    checkAuthStatus();
}

// 3. COMUNICAÇÃO DE CHAT COM A OLÍVIA
function setupChatListeners() {
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message-input");
    const newChatBtn = document.getElementById("new-chat-btn");
    const typingIndicator = document.getElementById("typing-indicator");

    if (newChatBtn) {
        newChatBtn.addEventListener("click", () => {
            localStorage.removeItem("olivia_conversation_id");
            currentConversationId = null;
            const chatBox = document.getElementById("chat-messages");
            if (chatBox) {
                chatBox.innerHTML = `
                    <div class="message-row bot">
                        <div class="avatar">✨</div>
                        <div class="message-bubble">
                            Nova conversa iniciada! Como posso ajudar você agora?
                        </div>
                    </div>
                `;
            }
        });
    }

    if (chatForm) {
        chatForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const messageText = messageInput.value.trim();
            if (!messageText) return;

            appendMessage("user", messageText);
            messageInput.value = "";
            if (typingIndicator) typingIndicator.classList.remove("hidden");

            try {
                const response = await fetch(`${API_BASE_URL}/api/chat`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${currentUser?.access_token}`
                    },
                    body: JSON.stringify({
                        message: messageText,
                        user_id: currentUser ? currentUser.user_id : 1,
                        conversation_id: currentConversationId
                    })
                });

                const data = await response.json();
                if (typingIndicator) typingIndicator.classList.add("hidden");

                if (response.ok) {
                    if (data.conversation_id) {
                        currentConversationId = data.conversation_id;
                        localStorage.setItem("olivia_conversation_id", data.conversation_id);
                    }
                    appendMessage("bot", data.response);
                } else {
                    appendMessage("bot", "Desculpe, tive uma instabilidade ao processar sua resposta.");
                }
            } catch (err) {
                if (typingIndicator) typingIndicator.classList.add("hidden");
                appendMessage("bot", "Erro ao conectar com a Olívia na nuvem.");
            }
        });
    }
}

// Renderiza mensagens com suporte a Markdown rico (listas, negritos, tópicos)
function appendMessage(sender, text) {
    const chatMessages = document.getElementById("chat-messages");
    if (!chatMessages) return;

    const rowDiv = document.createElement("div");
    rowDiv.classList.add("message-row", sender);

    const avatarDiv = document.createElement("div");
    avatarDiv.classList.add("avatar");
    avatarDiv.textContent = sender === "user" ? (currentUser?.name ? currentUser.name.charAt(0).toUpperCase() : "U") : "✨";

    const bubbleDiv = document.createElement("div");
    bubbleDiv.classList.add("message-bubble");

    // Converte Markdown em HTML formatado com a biblioteca marked
    if (typeof marked !== "undefined" && sender === "bot") {
        bubbleDiv.innerHTML = marked.parse(text);
    } else {
        bubbleDiv.textContent = text;
    }

    rowDiv.appendChild(avatarDiv);
    rowDiv.appendChild(bubbleDiv);

    chatMessages.appendChild(rowDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// MÓDULO DE TAREFAS CONECTADO AO BANCO
function setupTasksListeners() {
    const addTaskBtn = document.getElementById("add-task-btn");
    const taskInput = document.getElementById("new-task-input");

    if (addTaskBtn) {
        addTaskBtn.addEventListener("click", async () => {
            const title = taskInput.value.trim();
            if (!title) return;

            const userId = currentUser ? currentUser.user_id : 1;
            try {
                await fetch(`${API_BASE_URL}/api/tasks`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ title, user_id: userId })
                });
                taskInput.value = "";
                fetchTasks();
            } catch (err) {
                console.error("Erro ao salvar tarefa no banco.");
            }
        });
    }
}

async function fetchTasks() {
    const userId = currentUser ? currentUser.user_id : 1;
    try {
        const response = await fetch(`${API_BASE_URL}/api/tasks/${userId}`);
        if (response.ok) {
            tasks = await response.json();
            renderTasks();
        }
    } catch (err) {
        console.error("Erro ao buscar tarefas.");
    }
}

function renderTasks() {
    const tasksList = document.getElementById("tasks-list");
    if (!tasksList) return;

    tasksList.innerHTML = "";
    tasks.forEach(task => {
        const li = document.createElement("li");
        li.className = `task-item ${task.completed ? "completed" : ""}`;
        li.innerHTML = `
            <span>${task.title}</span>
            <button onclick="toggleTask(${task.id}, ${!task.completed})">${task.completed ? "✔ Concluída" : "Concluir"}</button>
        `;
        tasksList.appendChild(li);
    });
}

window.toggleTask = async function(id, completed) {
    try {
        await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ completed })
        });
        fetchTasks();
    } catch (err) {
        console.error("Erro ao atualizar tarefa.");
    }
};

// DIÁRIO DE HUMOR CONECTADO AO BANCO
function setupMoodListeners() {
    const moodBtns = document.querySelectorAll(".mood-btn");
    const moodResponse = document.getElementById("mood-response");

    moodBtns.forEach(btn => {
        btn.addEventListener("click", async () => {
            const mood = btn.getAttribute("data-mood");
            const userId = currentUser ? currentUser.user_id : 1;

            try {
                await fetch(`${API_BASE_URL}/api/mood`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ mood, user_id: userId })
                });
                if (moodResponse) moodResponse.classList.remove("hidden");
            } catch (err) {
                console.error("Erro ao salvar humor.");
            }
        });
    });
}