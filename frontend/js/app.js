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

// 1. CONTROLADOR DE SESSÃO E TELAS (SPA)
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

// Função auxiliar para exibir mensagens visuais de status sem alert()
function showAuthMessage(message, type = "error") {
    const alertBox = document.getElementById("auth-message");
    if (!alertBox) return;

    alertBox.textContent = message;
    alertBox.className = `auth-alert ${type}`;
    alertBox.classList.remove("hidden");
}

function hideAuthMessage() {
    const alertBox = document.getElementById("auth-message");
    if (alertBox) alertBox.classList.add("hidden");
}

// 2. AUTENTICAÇÃO COM COMPATIBILIDADE DE ROTAS E MENSAGENS VISUAIS
function setupAuthListeners() {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const showRegister = document.getElementById("show-register");
    const showLogin = document.getElementById("show-login");
    const logoutBtn = document.getElementById("logout-btn");

    if (showRegister) {
        showRegister.addEventListener("click", (e) => {
            e.preventDefault();
            hideAuthMessage();
            loginForm.classList.add("hidden");
            registerForm.classList.remove("hidden");
        });
    }

    if (showLogin) {
        showLogin.addEventListener("click", (e) => {
            e.preventDefault();
            hideAuthMessage();
            registerForm.classList.add("hidden");
            loginForm.classList.remove("hidden");
        });
    }

    // REGISTRO DE CONTA
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            hideAuthMessage();

            const name = document.getElementById("reg-name").value;
            const email = document.getElementById("reg-email").value;
            const password = document.getElementById("reg-password").value;

            try {
                // Tentativa na rota padrão /auth/register
                let response = await fetch(`${API_BASE_URL}/auth/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, email, password })
                });

                // Fallback automático para a rota /register caso o backend não use prefixo
                if (response.status === 404) {
                    response = await fetch(`${API_BASE_URL}/register`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ name, email, password })
                    });
                }

                const data = await response.json();

                if (response.ok) {
                    showAuthMessage("Conta criada com sucesso! Redirecionando para login...", "success");
                    setTimeout(() => {
                        hideAuthMessage();
                        registerForm.classList.add("hidden");
                        loginForm.classList.remove("hidden");
                    }, 2000);
                } else {
                    showAuthMessage(data.detail || "Não foi possível criar a conta.", "error");
                }
            } catch (err) {
                showAuthMessage("Erro ao conectar ao servidor. O serviço pode estar inicializando.", "error");
            }
        });
    }

    // LOGIN
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            hideAuthMessage();

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
                    showAuthMessage(data.detail || "E-mail ou senha incorretos.", "error");
                }
            } catch (err) {
                showAuthMessage("Servidor inacessível no momento. Tente novamente em instantes.", "error");
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
                        "Content-Type": "application/json"
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
                    appendMessage("bot", "Desculpe, tive uma instabilidade ao processar a resposta.");
                }
            } catch (err) {
                if (typingIndicator) typingIndicator.classList.add("hidden");
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

    if (typeof marked !== "undefined" && sender === "bot") {
        bubbleDiv.innerHTML = marked.parse(text);
    } else {
        let formattedText = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n\* /g, '<br>• ');
        bubbleDiv.innerHTML = `<p>${formattedText}</p>`;
    }

    rowDiv.appendChild(avatarDiv);
    rowDiv.appendChild(bubbleDiv);

    chatMessages.appendChild(rowDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 4. MÓDULO DE TAREFAS (CORRIGIDO)
function setupTasksListeners() {
    const addTaskBtn = document.getElementById("add-task-btn");
    const taskInput = document.getElementById("new-task-input");

    const handleAddTask = async () => {
        const title = taskInput.value.trim();
        if (!title) return;

        const newTask = { id: Date.now(), title, completed: false };
        tasks.push(newTask);
        localStorage.setItem("olivia_tasks", JSON.stringify(tasks));
        taskInput.value = "";
        renderTasks();

        // Tenta sincronizar com o banco em segundo plano
        try {
            await fetch(`${API_BASE_URL}/api/tasks`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title, user_id: currentUser ? currentUser.user_id : 1 })
            });
        } catch (e) {
            console.log("Sincronização offline das tarefas ativada.");
        }
    };

    if (addTaskBtn) {
        addTaskBtn.addEventListener("click", handleAddTask);
    }

    if (taskInput) {
        taskInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                handleAddTask();
            }
        });
    }
}

function renderTasks() {
    const tasksList = document.getElementById("tasks-list");
    if (!tasksList) return;

    tasksList.innerHTML = "";
    if (tasks.length === 0) {
        tasksList.innerHTML = `<li style="padding: 12px; color: #64748b;">Nenhuma meta cadastrada ainda. Adicione a primeira acima!</li>`;
        return;
    }

    tasks.forEach(task => {
        const li = document.createElement("li");
        li.className = `task-item ${task.completed ? "completed" : ""}`;
        li.innerHTML = `
            <span>${task.title}</span>
            <button class="btn-secondary" onclick="toggleTask(${task.id})">${task.completed ? "✔ Concluída" : "Concluir"}</button>
        `;
        tasksList.appendChild(li);
    });
}

window.toggleTask = function(id) {
    tasks = tasks.map(t => t.id === id ? { ...t, completed: !t.completed } : t);
    localStorage.setItem("olivia_tasks", JSON.stringify(tasks));
    renderTasks();
};

// 5. EXERCÍCIO DE RESPIRAÇÃO (CORRIGIDO)
function setupBreathingListeners() {
    const startBtn = document.getElementById("start-breathing-btn");
    const circle = document.getElementById("breathing-circle");
    const text = document.getElementById("breathing-text");

    if (startBtn) {
        startBtn.addEventListener("click", () => {
            startBtn.disabled = true;
            let cycles = 0;

            function runCycle() {
                if (!circle || !text) return;
                
                // Passagem 1: Inspire (4 seg)
                text.textContent = "Inspire devagar...";
                circle.classList.remove("exhale");
                circle.classList.add("inhale");

                setTimeout(() => {
                    // Passagem 2: Segure (4 seg)
                    text.textContent = "Segure o ar...";

                    setTimeout(() => {
                        // Passagem 3: Expire (4 seg)
                        text.textContent = "Expire suavemente...";
                        circle.classList.remove("inhale");
                        circle.classList.add("exhale");

                        setTimeout(() => {
                            cycles++;
                            if (cycles < 3) {
                                runCycle();
                            } else {
                                text.textContent = "Excelente! Como se sente?";
                                circle.classList.remove("exhale");
                                startBtn.disabled = false;
                            }
                        }, 4000);
                    }, 4000);
                }, 4000);
            }

            runCycle();
        });
    }
}

// 6. DIÁRIO DE HUMOR (CORRIGIDO COM REDIRECIONAMENTO E FEEDBACK)
function setupMoodListeners() {
    const moodBtns = document.querySelectorAll(".mood-btn");
    const moodResponse = document.getElementById("mood-response");

    moodBtns.forEach(btn => {
        btn.addEventListener("click", async () => {
            const mood = btn.getAttribute("data-mood");
            
            if (moodResponse) {
                moodResponse.classList.remove("hidden");
                moodResponse.innerHTML = `
                    <p style="margin-bottom: 12px;">Você registrou que está se sentindo <strong>${mood}</strong> hoje.</p>
                    <button id="chat-about-mood" class="btn-primary" style="margin-top: 8px;">Conversar com a Olívia sobre isso</button>
                `;

                const chatMoodBtn = document.getElementById("chat-about-mood");
                if (chatMoodBtn) {
                    chatMoodBtn.addEventListener("click", () => {
                        // Muda para a aba de chat e envia mensagem automática
                        const chatTabBtn = document.querySelector('[data-tab="tab-chat"]');
                        if (chatTabBtn) chatTabBtn.click();
                        
                        const msgInput = document.getElementById("message-input");
                        if (msgInput) {
                            msgInput.value = `Hoje estou me sentindo ${mood.toLowerCase()}. O que podemos fazer?`;
                        }
                    });
                }
            }

            // Grava no banco
            try {
                await fetch(`${API_BASE_URL}/api/mood`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ mood, user_id: currentUser ? currentUser.user_id : 1 })
                });
            } catch (err) {
                console.log("Humor salvo localmente.");
            }
        });
    });
}