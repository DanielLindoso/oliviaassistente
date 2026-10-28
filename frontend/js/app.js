// URL base da API no Render
const API_BASE_URL = "https://olivia-fskx.onrender.com";

// Tenta recuperar os dados da sessão do localStorage
let currentUser = JSON.parse(localStorage.getItem("olivia_user")) || null;
let currentConversationId = localStorage.getItem("olivia_conversation_id") || null;

document.addEventListener("DOMContentLoaded", () => {
    setupAuthListeners();
    setupChatListeners();
    checkAuthStatus();
});

// 1. Gerenciamento do estado da interface (Logado x Não Logado)
// 1. Gerenciamento do estado da interface (Logado x Não Logado)
function checkAuthStatus() {
    const authSection = document.getElementById("auth-container");
    const chatSection = document.getElementById("chat-container");
    const userDisplay = document.getElementById("user-name-display");

    // Se estiver na página chat.html, exibe sempre a área do chat
    if (chatSection) {
        chatSection.style.display = "flex";
    }

    if (currentUser && currentUser.name && userDisplay) {
        userDisplay.textContent = `Olá, ${currentUser.name}!`;
    }
}

// 2. Eventos de Cadastro, Login e Logout
function setupAuthListeners() {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const logoutBtn = document.getElementById("logout-btn");

    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const name = document.getElementById("reg-name").value;
            const email = document.getElementById("reg-email").value;
            const password = document.getElementById("reg-password").value;

            try {
                const response = await fetch(`${API_BASE_URL}/auth/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name, email, password })
                });

                const data = await response.json();
                if (response.ok) {
                    alert("Conta criada com sucesso! Faça login para continuar.");
                    registerForm.reset();
                } else {
                    alert(`Erro: ${data.detail}`);
                }
            } catch (err) {
                alert("Erro ao conectar ao servidor. Tente novamente.");
            }
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value;
            const password = document.getElementById("login-password").value;

            try {
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();
                if (response.ok) {
                    currentUser = data;
                    localStorage.setItem("olivia_user", JSON.stringify(data));
                    checkAuthStatus();
                } else {
                    alert(`Erro: ${data.detail}`);
                }
            } catch (err) {
                alert("Erro de conexão ao fazer login.");
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

// 3. Envio de Mensagens do Chat
function setupChatListeners() {
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message-input");
    const chatMessages = document.getElementById("chat-messages");

    if (chatForm) {
        chatForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const messageText = messageInput.value.trim();
            if (!messageText) return;

            // Renderiza mensagem do usuário
            appendMessage("user", messageText);
            messageInput.value = "";

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

                if (response.ok) {
                    if (data.conversation_id) {
                        currentConversationId = data.conversation_id;
                        localStorage.setItem("olivia_conversation_id", data.conversation_id);
                    }
                    appendMessage("assistant", data.response);
                } else {
                    appendMessage("assistant", "Desculpe, não consegui processar sua mensagem agora.");
                }
            } catch (err) {
                appendMessage("assistant", "Erro de conexão com a Olívia.");
            }
        });
    }

    function appendMessage(sender, text) {
        if (!chatMessages) return;
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message", sender === "user" ? "user-message" : "bot-message");
        msgDiv.textContent = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}