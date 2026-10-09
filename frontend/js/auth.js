// ============ AUTH UTILITY ============
// Simple hash for demo (NOT cryptographically secure)
function simpleHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        const char = str.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return "h" + Math.abs(hash).toString(36);
}

// ============ USER STORAGE ============
function getUsers() {
    const users = localStorage.getItem("ir_prohori_users");
    return users ? JSON.parse(users) : {};
}

function saveUsers(users) {
    localStorage.setItem("ir_prohori_users", JSON.stringify(users));
}

function findUserByEmail(email) {
    const users = getUsers();
    const emailLower = email.trim().toLowerCase();
    for (const id in users) {
        if (users[id].email.toLowerCase() === emailLower) {
            return { id, user: users[id] };
        }
    }
    return null;
}

// ============ SESSION ============
function getCurrentUser() {
    const data = localStorage.getItem("ir_prohori_user");
    return data ? JSON.parse(data) : null;
}

function setCurrentUser(user) {
    localStorage.setItem("ir_prohori_user", JSON.stringify(user));
}

function logoutUser() {
    localStorage.removeItem("ir_prohori_user");
}