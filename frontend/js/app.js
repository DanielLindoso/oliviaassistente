const API_BASE_URL = "https://olivia-fskx.onrender.com";

let currentUser = JSON.parse(localStorage.getItem("olivia_user")) || null;
let currentConversationId = localStorage.getItem("olivia_conversation_id") || null;

document.addEventListener("DOMContentLoaded", () => {
    setupAuthListeners();
    setupChatListeners();
    checkAuthStatus();
});

function checkAuthStatus() {
    const userDisplay = document.getElementById("user-name-display");
    const userAvatar = document.getElementById("user-avatar");

    if (currentUser && currentUser.name) {
        if (userDisplay) userDisplay.textContent = currentUser.name;
        if (userAvatar) userAvatar.textContent = currentUser.name.charAt(0).toUpperCase();
    }
}

function setupAuthListeners() {
    const logoutBtn = document.getElementById("logout-btn");
    const newChatBtn = document.getElementById("new-chat-btn");

    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("olivia_user");
            localStorage.removeItem("olivia_conversation_id");
            window.location.href = "index.html";
        });
    }

    if (newChatBtn) {
        newChatBtn.addEventListener("click", () => {
            localStorage.removeItem("olivia_conversation_id");
            currentConversationId = null;
            const chatMessages = document.getElementById("chat-messages");
            if (chatMessages) {
                chatMessages.innerHTML = `
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
}

function setupChatListeners() {
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message-input");

    if (chatForm) {
        chatForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const messageText = messageInput.value.trim();
            if (!messageText) return;

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
                    appendMessage("bot", data.response);
                } else {
                    appendMessage("bot", "Desculpe, não consegui processar sua mensagem agora.");
                }
            } catch (err) {
                appendMessage("bot", "Erro de conexão com o servidor da Olívia.");
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
    
    if (sender === "user") {
        avatarDiv.textContent = currentUser?.name ? currentUser.name.charAt(0).toUpperCase() : "U";
    } else {
        avatarDiv.textContent = "✨";
    }

    const bubbleDiv = document.createElement("div");
    bubbleDiv.classList.add("message-bubble");
    bubbleDiv.textContent = text;

    rowDiv.appendChild(avatarDiv);
    rowDiv.appendChild(bubbleDiv);

    chatMessages.appendChild(rowDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}