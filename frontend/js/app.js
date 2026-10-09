// ============ CONFIG ============
const API_URL = "http://127.0.0.1:8000/chat";

// ============ STATE ============
let chats = {};
let currentChatId = null;
let isWaiting = false;

// ============ DOM ELEMENTS ============
const welcomeScreen = document.getElementById("welcomeScreen");
const chatContainer = document.getElementById("chatContainer");
const chatList = document.getElementById("chatList");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const newChatBtn = document.getElementById("newChatBtn");
const sidebar = document.getElementById("sidebar");
const sidebarOverlay = document.getElementById("sidebarOverlay");
const hamburgerBtn = document.getElementById("hamburgerBtn");
const sidebarCloseBtn = document.getElementById("sidebarCloseBtn");

// ============ MARKDOWN PARSER ============
function parseMarkdown(text) {
    let html = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/(?<!\*)\*([^*\n]+?)\*(?!\*)/g, "<em>$1</em>");

    const lines = html.split("\n");
    const out = [];
    let inList = false;

    for (let line of lines) {
        const trimmed = line.trim();

        const numMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
        if (numMatch) {
            if (!inList) {
                out.push('<ol class="md-list">');
                inList = true;
            }
            out.push(`<li>${numMatch[2]}</li>`);
            continue;
        }

        const bulletMatch = trimmed.match(/^[-•]\s+(.*)$/);
        if (bulletMatch) {
            if (!inList) {
                out.push('<ul class="md-list">');
                inList = true;
            }
            out.push(`<li>${bulletMatch[1]}</li>`);
            continue;
        }

        if (inList) {
            out.push(inList === true ? "</ol>" : "</ul>");
            inList = false;
        }

        if (trimmed === "") {
            out.push('<div class="md-spacer"></div>');
        } else {
            out.push(`<p class="md-p">${trimmed}</p>`);
        }
    }

    if (inList) {
        out.push(inList === true ? "</ol>" : "</ul>");
    }

    return out.join("");
}

// ============ INIT ============
function init() {
    displayUser();
    loadChats();
    setupSidebar();
    setupLogout();
    renderChatList();
    updateSendButton();
}

// ============ USER DISPLAY ============
function displayUser() {
    const userData = localStorage.getItem("ir_prohori_user");
    if (!userData) {
        window.location.href = "login.html";
        return;
    }

    const user = JSON.parse(userData);
    const userName = document.getElementById("userName");
    const userRole = document.getElementById("userRole");
    const userAvatar = document.getElementById("userAvatar");

    if (userName) {
        userName.textContent = user.name;
        userName.title = user.name;
    }
    if (userRole) {
        userRole.innerHTML = `<span class="role-badge">${user.role}</span> <span style="color: #6a6a6a;">• #DigitalProhori</span>`;
    }
    if (userAvatar) {
        userAvatar.textContent = user.name.charAt(0).toUpperCase();
        userAvatar.title = user.name;
    }
}

// ============ SIDEBAR (MOBILE) ============
function setupSidebar() {
    if (hamburgerBtn) {
        hamburgerBtn.addEventListener("click", () => {
            sidebar.classList.add("open");
            sidebarOverlay.classList.add("active");
        });
    }
    if (sidebarCloseBtn) sidebarCloseBtn.addEventListener("click", closeSidebar);
    if (sidebarOverlay) sidebarOverlay.addEventListener("click", closeSidebar);
}

function closeSidebar() {
    sidebar.classList.remove("open");
    sidebarOverlay.classList.remove("active");
}

// ============ LOGOUT ============
function setupLogout() {
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            if (confirm("Are you sure you want to sign out?")) {
                localStorage.removeItem("ir_prohori_user");
                window.location.href = "login.html";
            }
        });
    }
}

// ============ LOAD CHATS ============
function loadChats() {
    const saved = localStorage.getItem("ir_prohori_chats");
    if (saved) {
        try {
            chats = JSON.parse(saved);
            currentChatId = localStorage.getItem("ir_prohori_current") || null;
        } catch (e) {
            chats = {};
        }
    }

    if (!currentChatId || !chats[currentChatId]) {
        createNewChat();
    } else {
        renderChat();
    }
}

// ============ SAVE / LOAD ============
function saveState() {
    localStorage.setItem("ir_prohori_chats", JSON.stringify(chats));
    localStorage.setItem("ir_prohori_current", currentChatId);
}

// ============ CHAT MANAGEMENT ============
function createNewChat() {
    const id = "chat_" + Date.now();
    chats[id] = {
        title: "New Chat",
        messages: [],
        created: new Date().toISOString()
    };
    currentChatId = id;
    saveState();
    renderChatList();
    renderChat();
    if (messageInput) messageInput.focus();
    closeSidebar();
}

// ============ DELETE CHAT ============
function deleteChat(chatId, event) {
    event.stopPropagation();

    const chat = chats[chatId];
    if (!chat) return;

    if (!confirm(`Delete this chat: "${chat.title}"?`)) return;

    delete chats[chatId];

    if (currentChatId === chatId) {
        const remaining = Object.keys(chats);
        if (remaining.length > 0) {
            currentChatId = remaining[remaining.length - 1];
        } else {
            createNewChat();
            return;
        }
    }

    saveState();
    renderChatList();
    renderChat();
}

function renderChatList() {
    chatList.innerHTML = "";
    const ids = Object.keys(chats).reverse();

    if (ids.length === 0) {
        chatList.innerHTML = '<div style="padding:12px;color:#6a6a6a;font-size:12.5px;">No chats yet</div>';
        return;
    }

    ids.forEach(id => {
        const chat = chats[id];

        const wrapper = document.createElement("div");
        wrapper.className = "chat-item-wrapper";

        const div = document.createElement("div");
        div.className = "chat-item" + (id === currentChatId ? " active" : "");
        div.textContent = chat.title;
        div.title = chat.title;
        div.onclick = () => {
            currentChatId = id;
            saveState();
            renderChatList();
            renderChat();
            closeSidebar();
        };

        const delBtn = document.createElement("button");
        delBtn.className = "chat-delete-btn";
        delBtn.innerHTML = "🗑";
        delBtn.title = "Delete chat";
        delBtn.onclick = (e) => deleteChat(id, e);

        wrapper.appendChild(div);
        wrapper.appendChild(delBtn);
        chatList.appendChild(wrapper);
    });
}

function renderChat() {
    const chat = chats[currentChatId];
    if (!chat) return;

    if (chat.messages.length === 0) {
        welcomeScreen.style.display = "flex";
        chatContainer.classList.remove("active");
        chatContainer.innerHTML = "";
        return;
    }

    welcomeScreen.style.display = "none";
    chatContainer.classList.add("active");
    chatContainer.innerHTML = "";

    chat.messages.forEach(msg => {
        appendMessage(msg.role, msg.content, msg.sources, msg.sourceType, false);
    });

    scrollToBottom();
}

// ============ MESSAGE RENDERING ============
function appendMessage(role, content, sources = [], sourceType = "general", shouldSave = true) {
    welcomeScreen.style.display = "none";
    chatContainer.classList.add("active");

    const row = document.createElement("div");
    row.className = "message-row " + role;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";

    if (role === "user") {
        const userData = localStorage.getItem("ir_prohori_user");
        if (userData) {
            const user = JSON.parse(userData);
            avatar.textContent = user.name.charAt(0).toUpperCase();
        } else {
            avatar.textContent = "U";
        }
    } else {
        avatar.textContent = "🛡️";
    }

    const msgContent = document.createElement("div");
    msgContent.className = "message-content";

    const answerDiv = document.createElement("div");
    answerDiv.className = "md-content";
    if (role === "user") {
        answerDiv.textContent = content;
    } else {
        answerDiv.innerHTML = parseMarkdown(content);
    }
    msgContent.appendChild(answerDiv);

    if (role === "assistant") {
        if (sourceType === "verified" && sources.length > 0) {
            const badge = document.createElement("div");
            badge.className = "source-badge verified-badge";
            badge.innerHTML = "✓ Verified from our library";
            msgContent.appendChild(badge);

            const sourceBox = document.createElement("div");
            sourceBox.className = "source-box";

            const header = document.createElement("div");
            header.className = "source-header";
            header.textContent = "📄 Sources";
            sourceBox.appendChild(header);

            sources.forEach(s => {
                const item = document.createElement("div");
                item.className = "source-item";
                item.innerHTML = `<strong>${s.name}</strong>`;
                sourceBox.appendChild(item);
            });

            msgContent.appendChild(sourceBox);
        } else if (sourceType === "general") {
            const badge = document.createElement("div");
            badge.className = "source-badge general-badge";
            badge.innerHTML = "ℹ️ General knowledge, not from verified library";
            msgContent.appendChild(badge);
        }
    }

    if (role === "user") {
        row.appendChild(msgContent);
        row.appendChild(avatar);
    } else {
        row.appendChild(avatar);
        row.appendChild(msgContent);
    }

    chatContainer.appendChild(row);

    if (shouldSave) {
        const chat = chats[currentChatId];
        chat.messages.push({ role, content, sources, sourceType });
        saveState();
    }

    scrollToBottom();
}

function showTypingIndicator() {
    const row = document.createElement("div");
    row.className = "message-row assistant";
    row.id = "typingRow";

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = "🛡️";

    const indicator = document.createElement("div");
    indicator.className = "message-content";
    indicator.innerHTML = `
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    `;

    row.appendChild(avatar);
    row.appendChild(indicator);
    chatContainer.appendChild(row);
    scrollToBottom();
}

function removeTypingIndicator() {
    const el = document.getElementById("typingRow");
    if (el) el.remove();
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ============ SEND MESSAGE ============
async function sendMessage(text) {
    if (!text.trim() || isWaiting) return;
    isWaiting = true;
    updateSendButton();

    const chat = chats[currentChatId];

    if (chat.title === "New Chat") {
        chat.title = text.length > 28 ? text.substring(0, 28) + "..." : text;
        renderChatList();
    }

    appendMessage("user", text);
    messageInput.value = "";
    messageInput.style.height = "auto";

    showTypingIndicator();

    // 🧠 Detect and save user facts
    detectAndSaveMemory(text);

    try {
        const userData = JSON.parse(localStorage.getItem("ir_prohori_user") || "{}");

        const history = chat.messages
            .filter(m => m.role === "user" || m.role === "assistant")
            .slice(-6)
            .map(m => ({ role: m.role, content: m.content }));

        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: text,
                role: userData.role || "Student",
                chat_id: currentChatId,
                history: history,
                memory: getMemoryContext()
            })
        });

        if (!response.ok) throw new Error("Server error");

        const data = await response.json();
        removeTypingIndicator();
        appendMessage("assistant", data.answer, data.sources || [], data.source_type || "general");

    } catch (error) {
        removeTypingIndicator();
        appendMessage("assistant", "Sorry, something went wrong. Please check if the backend is running. Error: " + error.message);
    }

    isWaiting = false;
    updateSendButton();
}

// ============ INPUT HANDLERS ============
function updateSendButton() {
    sendBtn.disabled = !messageInput.value.trim() || isWaiting;
}

messageInput.addEventListener("input", () => {
    messageInput.style.height = "auto";
    messageInput.style.height = Math.min(messageInput.scrollHeight, 200) + "px";
    updateSendButton();
});

messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(messageInput.value);
    }
});

sendBtn.addEventListener("click", () => sendMessage(messageInput.value));

newChatBtn.addEventListener("click", () => {
    createNewChat();
});

// ============ SUGGESTION CARDS ============
document.querySelectorAll(".suggestion-card").forEach(card => {
    card.addEventListener("click", () => {
        const query = card.getAttribute("data-query");
        if (query) {
            sendMessage(query);
        }
    });
});

// ============ START ============
init();