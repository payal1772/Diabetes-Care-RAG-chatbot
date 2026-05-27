function getStoredToken() {
    const token = localStorage.getItem("token");

    if (!token || token === "undefined" || token === "null" || token.split(".").length !== 3) {
        localStorage.removeItem("token");
        localStorage.removeItem("name");
        return null;
    }

    return token;
}

const token = getStoredToken();

if (!token) {
    window.location.href = "login.html";
}

async function readJsonResponse(response) {
    const text = await response.text();

    if (!text) {
        return {};
    }

    try {
        return JSON.parse(text);
    } catch (error) {
        throw new Error(`Backend returned a non-JSON response with status ${response.status}`);
    }
}

async function sendMessage() {
    const messageInput = document.getElementById("message");
    const sendButton = document.getElementById("sendButton");
    const message = messageInput.value.trim();

    const glucose = document.getElementById("glucose").value;
    const meal = document.getElementById("meal").value;
    const sleep = document.getElementById("sleep").value;
    const water = document.getElementById("water").value;
    const steps = document.getElementById("steps").value;
    const symptoms = document.getElementById("symptoms").value;

    if (!message) return;

    addMessage(message, "user-message", "You");
    messageInput.value = "";
    resizeComposer(messageInput);
    sendButton.disabled = true;
    sendButton.innerText = "Sending";

    const thinkingBubble = addMessage("Thinking", "bot-message thinking", "Assistant");

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({
                message: message,
                glucose: glucose,
                meal: meal,
                sleep: sleep,
                water: water,
                steps: steps,
                symptoms: symptoms
            })
        });

        const data = await readJsonResponse(res);

        if (res.status === 401) {
            localStorage.removeItem("token");
            localStorage.removeItem("name");
            window.location.href = "login.html";
            return;
        }

        if (!res.ok) {
            throw new Error(data.error || "Backend request failed");
        }

    let finalAnswer = data.answer || "The backend replied, but no answer was returned.";

    if (data.sources && data.sources.length > 0) {
        finalAnswer += "\n\nSources Used:";

        data.sources.forEach((source, index) => {
            finalAnswer += `\n${index + 1}. ${source.substring(0, 120)}...`;
        });
    }

    updateMessage(thinkingBubble, finalAnswer, "Assistant");
    scrollToBottom();
        } catch (error) {
            const message = error instanceof TypeError
                ? "I could not connect to Flask. Make sure the backend server is running at http://127.0.0.1:5000/."
                : error.message;

            updateMessage(
                thinkingBubble,
                message,
                "Assistant"
            );
        } finally {
        thinkingBubble.classList.remove("thinking");
        sendButton.disabled = false;
        sendButton.innerText = "Send";
        messageInput.focus();
        scrollToBottom();
        }
    }

function addMessage(text, className, label) {
    const chatBox = document.getElementById("chatBox");

    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${className}`;
    updateMessage(messageDiv, text, label);

    chatBox.appendChild(messageDiv);
    scrollToBottom();

    return messageDiv;
}

function updateMessage(messageDiv, text, label) {
    messageDiv.innerHTML = "";

    const labelSpan = document.createElement("span");
    labelSpan.className = "message-label";
    labelSpan.innerText = label;

    const textSpan = document.createElement("span");
    textSpan.innerText = text;

    messageDiv.appendChild(labelSpan);
    messageDiv.appendChild(textSpan);
}

function scrollToBottom() {
    const chatBox = document.getElementById("chatBox");
    chatBox.scrollTop = chatBox.scrollHeight;
}

document.getElementById("chatForm").addEventListener("submit", function(event) {
    event.preventDefault();
    sendMessage();
});

document.getElementById("message").addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

document.getElementById("message").addEventListener("input", function(event) {
    resizeComposer(event.target);
});

document.querySelectorAll(".quick-prompts button").forEach((button) => {
    button.addEventListener("click", function() {
        const messageInput = document.getElementById("message");
        messageInput.value = this.dataset.prompt;
        resizeComposer(messageInput);
        messageInput.focus();
    });
});

function resizeComposer(textarea) {
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
}

resizeComposer(document.getElementById("message"));

function logoutUser() {
    localStorage.removeItem("token");
    localStorage.removeItem("name");
    window.location.href = "login.html";
}
