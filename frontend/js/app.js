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

// 1. GERENCIAMENTO DE TELAS E NAVEGAÇÃO SPA
function checkAuthStatus() {
    const authScreen = document.getElementById("auth-screen");
    const mainApp = document.getElementById("main-app");
    const userDisplay = document.getElementById("user-name-display");
    const userAvatar = document.getElementById("user-avatar");

    if (currentUser && currentUser.name) {
        authScreen.classList.add("hidden");
        mainApp.classList.remove("hidden");
        if (userDisplay) userDisplay.textContent = currentUser.name;
        if (userAvatar) userAvatar.textContent = currentUser.name.charAt(0).toUpperCase();
        renderTasks();
    } else {
        authScreen.classList.remove("hidden");
        mainApp.classList.add("hidden");
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
            document.getElementById(targetTab).classList.remove("hidden");
        });
    });
}

// 2. AUTENTICAÇÃO (LOGIN & REGISTRO)
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
                // Tenta chamar a API do Render
                let response = await fetch(`${API_BASE_URL}/auth/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, email, password })
                });

                // Se der 404, tenta a rota alternativa sem o /auth/ na frente
                if (response.status === 404) {
                    response = await fetch(`${API_BASE_URL}/register`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ name, email, password })
                    });
                }

                const data = await response.json();
                if (response.ok) {
                    alert("Conta criada com sucesso! Faça login para entrar.");
                    registerForm.classList.add("hidden");
                    loginForm.classList.remove("hidden");
                } else {
                    alert(`Erro: ${data.detail || 'Não foi possível cadastrar.'}`);
                }
            } catch (err) {
                // Caso ocorra falha de rede/servidor offline, entra em modo local de teste
                alert("Criando sessão local de teste para navegação nas telas...");
                currentUser = { name, email, user_id: 1, access_token: "test_token" };
                localStorage.setItem("olivia_user", JSON.stringify(currentUser));
                checkAuthStatus();
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
                    alert(`Erro: ${data.detail || 'Falha na autenticação.'}`);
                }
            } catch (err) {
                // Fallback para testar o painel sem travar
                currentUser = { name: email.split("@")[0], email, user_id: 1, access_token: "test_token" };
                localStorage.setItem("olivia_user", JSON.stringify(currentUser));
                checkAuthStatus();
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

// 3. CHAT COM A OLÍVIA
function setupChatListeners() {
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message-input");
    const newChatBtn = document.getElementById("new-chat-btn");
    const typingIndicator = document.getElementById("typing-indicator");

    if (newChatBtn) {
        newChatBtn.addEventListener("click", () => {
            localStorage.removeItem("olivia_conversation_id");
            currentConversationId = null;
            document.getElementById("chat-messages").innerHTML = `
                <div class="message-row bot">
                    <div class="avatar">✨</div>
                    <div class="message-bubble">
                        Nova conversa iniciada! Como posso ajudar você agora?
                    </div>
                </div>
            `;
        });
    }

    if (chatForm) {
        chatForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const messageText = messageInput.value.trim();
            if (!messageText) return;

            appendMessage("user", messageText);
            messageInput.value = "";
            typingIndicator.classList.remove("hidden");

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
                typingIndicator.classList.add("hidden");

                if (response.ok) {
                    if (data.conversation_id) {
                        currentConversationId = data.conversation_id;
                        localStorage.setItem("olivia_conversation_id", data.conversation_id);
                    }
                    appendMessage("bot", data.response);
                } else {
                    appendMessage("bot", "Desculpe, tive uma instabilidade ao processar a resposta.");
                }
            } catch (err) {
                typingIndicator.classList.add("hidden");
                appendMessage("bot", "Erro ao conectar com a Olívia na nuvem.");
            }
        });
    }
}

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
    
    // Formatação básica de marcação (Markdown simples)
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n\* /g, '<br>• ');
    
    bubbleDiv.innerHTML = `<p>${formattedText}</p>`;

    rowDiv.appendChild(avatarDiv);
    rowDiv.appendChild(bubbleDiv);

    chatMessages.appendChild(rowDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 4. MÓDULO DE TAREFAS
function setupTasksListeners() {
    const addTaskBtn = document.getElementById("add-task-btn");
    const taskInput = document.getElementById("new-task-input");

    if (addTaskBtn) {
        addTaskBtn.addEventListener("click", () => {
            const title = taskInput.value.trim();
            if (!title) return;

            tasks.push({ id: Date.now(), title, completed: false });
            localStorage.setItem("olivia_tasks", JSON.stringify(tasks));
            taskInput.value = "";
            renderTasks();
        });
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
            <button onclick="toggleTask(${task.id})">${task.completed ? "✔ Concluída" : "Concluir"}</button>
        `;
        tasksList.appendChild(li);
    });
}

window.toggleTask = function(id) {
    tasks = tasks.map(t => t.id === id ? { ...t, completed: !t.completed } : t);
    localStorage.setItem("olivia_tasks", JSON.stringify(tasks));
    renderTasks();
};

// 5. EXERCÍCIO DE RESPIRAÇÃO
function setupBreathingListeners() {
    const startBtn = document.getElementById("start-breathing-btn");
    const circle = document.getElementById("breathing-circle");
    const text = document.getElementById("breathing-text");

    if (startBtn) {
        startBtn.addEventListener("click", () => {
            startBtn.disabled = true;
            text.textContent = "Inspire...";
            circle.classList.add("inhale");

            setTimeout(() => {
                text.textContent = "Segure...";
                setTimeout(() => {
                    text.textContent = "Expire...";
                    circle.classList.remove("inhale");
                    circle.classList.add("exhale");
                    setTimeout(() => {
                        text.textContent = "Concluído!";
                        startBtn.disabled = false;
                    }, 4000);
                }, 4000);
            }, 4000);
        });
    }
}

// 6. DIÁRIO DE HUMOR
function setupMoodListeners() {
    const moodBtns = document.querySelectorAll(".mood-btn");
    const moodResponse = document.getElementById("mood-response");

    moodBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            moodResponse.classList.remove("hidden");
        });
    });
}