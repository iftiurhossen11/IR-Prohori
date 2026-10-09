// Redirect if already logged in
if (localStorage.getItem("ir_prohori_user")) {
    window.location.href = "index.html";
}

const registerForm = document.getElementById("registerForm");
const nameInput = document.getElementById("nameInput");
const emailInput = document.getElementById("emailInput");
const roleSelect = document.getElementById("roleSelect");
const passwordInput = document.getElementById("passwordInput");
const confirmInput = document.getElementById("confirmInput");
const securityQuestion = document.getElementById("securityQuestion");
const securityAnswer = document.getElementById("securityAnswer");

registerForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const name = nameInput.value.trim();
    const email = emailInput.value.trim().toLowerCase();
    const role = roleSelect.value;
    const password = passwordInput.value;
    const confirm = confirmInput.value;
    const question = securityQuestion.value;
    const answer = securityAnswer.value.trim();

    // Validation
    if (!name || !email || !password || !answer) {
        alert("Please fill in all fields");
        return;
    }

    if (!email.includes("@") || !email.includes(".")) {
        alert("Please enter a valid email");
        return;
    }

    if (password.length < 6) {
        alert("Password must be at least 6 characters");
        return;
    }

    if (password !== confirm) {
        alert("Passwords do not match");
        return;
    }

    // Check existing user
    if (findUserByEmail(email)) {
        alert("This email is already registered. Please login.");
        return;
    }

    // Create user
    const userId = "user_" + Date.now();
    const users = getUsers();
    users[userId] = {
        name: name,
        email: email,
        role: role,
        passwordHash: simpleHash(password),
        securityQuestion: question,
        securityAnswerHash: simpleHash(answer.toLowerCase()),
        createdAt: new Date().toISOString()
    };
    saveUsers(users);

    // Auto login
    setCurrentUser({
        id: userId,
        name: name,
        email: email,
        role: role
    });

    alert("Account created successfully! Welcome to IR Prohori.");
    window.location.href = "index.html";
});