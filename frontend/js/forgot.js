const forgotForm = document.getElementById("forgotForm");
const emailInput = document.getElementById("emailInput");
const questionGroup = document.getElementById("questionGroup");
const answerGroup = document.getElementById("answerGroup");
const newPasswordGroup = document.getElementById("newPasswordGroup");
const questionDisplay = document.getElementById("questionDisplay");
const answerInput = document.getElementById("answerInput");
const newPasswordInput = document.getElementById("newPasswordInput");
const submitBtn = document.getElementById("submitBtn");

let currentStage = "find"; // find → answer → reset
let foundUser = null;
let foundUserId = null;

forgotForm.addEventListener("submit", (e) => {
    e.preventDefault();

    if (currentStage === "find") {
        const email = emailInput.value.trim().toLowerCase();

        if (!email) {
            alert("Please enter your email");
            return;
        }

        const result = findUserByEmail(email);
        if (!result) {
            alert("No account found with this email. Please register.");
            return;
        }

        foundUser = result.user;
        foundUserId = result.id;

        // Show question
        questionDisplay.value = foundUser.securityQuestion;
        questionGroup.style.display = "flex";
        answerGroup.style.display = "flex";
        emailInput.disabled = true;
        submitBtn.textContent = "Verify Answer";
        currentStage = "answer";

    } else if (currentStage === "answer") {
        const answer = answerInput.value.trim().toLowerCase();

        if (!answer) {
            alert("Please enter your answer");
            return;
        }

        if (simpleHash(answer) !== foundUser.securityAnswerHash) {
            alert("Incorrect answer. Please try again.");
            return;
        }

        // Show new password
        newPasswordGroup.style.display = "flex";
        answerInput.disabled = true;
        submitBtn.textContent = "Reset Password";
        currentStage = "reset";

    } else if (currentStage === "reset") {
        const newPassword = newPasswordInput.value;

        if (newPassword.length < 6) {
            alert("Password must be at least 6 characters");
            return;
        }

        // Update password
        const users = getUsers();
        users[foundUserId].passwordHash = simpleHash(newPassword);
        saveUsers(users);

        alert("Password reset successfully! Please login with your new password.");
        window.location.href = "login.html";
    }
});