const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const chatMessages = document.getElementById("chatMessages");
const sendButton = document.getElementById("sendButton");

const API_URL = "https://olivia-fskx.onrender.com/api/chat";


function adicionarMensagem(texto, tipo) {
    const message = document.createElement("div");
    message.classList.add("message");

    if (tipo === "olivia") {
        message.classList.add("message-olivia");

        message.innerHTML = `
            <div class="message-avatar">
                O
            </div>

            <div class="message-content">
                <span class="message-name">Olivia</span>

                <p>${texto}</p>
            </div>
        `;
    } else {
        message.classList.add("message-user");

        message.innerHTML = `
            <div class="message-content">
                <span class="message-name">Você</span>

                <p>${texto}</p>
            </div>
        `;
    }

    chatMessages.appendChild(message);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}


function mostrarCarregando() {
    const loading = document.createElement("div");

    loading.id = "loadingMessage";
    loading.classList.add("message", "message-olivia");

    loading.innerHTML = `
        <div class="message-avatar">
            O
        </div>

        <div class="message-content">
            <span class="message-name">Olivia</span>

            <p>Olivia está pensando...</p>
        </div>
    `;

    chatMessages.appendChild(loading);

    chatMessages.scrollTop = chatMessages.scrollHeight;
}


function removerCarregando() {
    const loading = document.getElementById("loadingMessage");

    if (loading) {
        loading.remove();
    }
}


async function enviarMensagem(mensagem) {
    const resposta = await fetch(API_URL, {
        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            message: mensagem
        })
    });

    if (!resposta.ok) {
        throw new Error("Erro ao comunicar com a API.");
    }

    return await resposta.json();
}


chatForm.addEventListener("submit", async function(event) {

    event.preventDefault();

    const mensagem = messageInput.value.trim();

    if (!mensagem) {
        return;
    }

    adicionarMensagem(mensagem, "usuario");

    messageInput.value = "";

    sendButton.disabled = true;
    messageInput.disabled = true;

    mostrarCarregando();

    try {

        const dados = await enviarMensagem(mensagem);

        removerCarregando();

        adicionarMensagem(dados.response, "olivia");

    } catch (erro) {

        removerCarregando();

        adicionarMensagem(
            "Desculpe, não consegui me conectar ao servidor. Verifique se a API da Olivia está funcionando.",
            "olivia"
        );

        console.error(erro);

    } finally {

        sendButton.disabled = false;
        messageInput.disabled = false;

        messageInput.focus();
    }

});