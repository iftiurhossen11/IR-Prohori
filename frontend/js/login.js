// Redirect if already logged in
if (localStorage.getItem("ir_prohori_user")) {
    window.location.href = "index.html";
}

const loginForm = document.getElementById("loginForm");
const emailInput = document.getElementById("emailInput");
const passwordInput = document.getElementById("passwordInput");

loginForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const email = emailInput.value.trim().toLowerCase();
    const password = passwordInput.value;

    if (!email || !password) {
        alert("Please fill in all fields");
        return;
    }

    const result = findUserByEmail(email);

    if (!result) {
        alert("No account found with this email.\nPlease register first.");
        window.location.href = "register.html";
        return;
    }

    if (result.user.passwordHash !== simpleHash(password)) {
        alert("Incorrect password. Please try again.");
        return;
    }

    // Login success
    setCurrentUser({
        id: result.id,
        name: result.user.name,
        email: result.user.email,
        role: result.user.role
    });

    window.location.href = "index.html";
});