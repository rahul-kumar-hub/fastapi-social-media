console.log("register.js loaded");
const form = document.getElementById("registerForm");
const button = form.querySelector("button");
const message = document.getElementById("message");

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    message.innerHTML = "";

    const username = document.getElementById("username");
    const email = document.getElementById("email");
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirmPassword");

    // Trim values
    username.value = username.value.trim();
    email.value = email.value.trim();

    // ---------- Validation ----------

    if (username.value.length < 3) {

        message.innerHTML = `
            <div class="alert alert-danger">
                Username must be at least 3 characters.
            </div>
        `;

        username.focus();
        return;
    }

    if (email.value === "") {

        message.innerHTML = `
            <div class="alert alert-danger">
                Email is required.
            </div>
        `;

        email.focus();
        return;
    }

    // Simple email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailRegex.test(email.value)) {

        message.innerHTML = `
            <div class="alert alert-danger">
                Enter a valid email address.
            </div>
        `;

        email.focus();
        return;
    }

    if (password.value.length < 8) {

        message.innerHTML = `
            <div class="alert alert-danger">
                Password must contain at least 8 characters.
            </div>
        `;

        password.focus();
        return;
    }

    if (password.value !== confirmPassword.value) {

        message.innerHTML = `
            <div class="alert alert-danger">
                Passwords do not match.
            </div>
        `;

        confirmPassword.focus();
        return;
    }

    // ---------- Loading ----------

    button.disabled = true;

    button.innerHTML = `
        <span class="spinner-border spinner-border-sm me-2"></span>
        Creating Account...
    `;

    try {

        const response = await fetch("/users/register", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                username: username.value,
                email: email.value,
                password: password.value

            })

        });

        const data = await response.json();

        if (response.ok) {

            form.reset();

            message.innerHTML = `
                <div class="alert alert-success">
                    ✔ Account created successfully.<br>
                    Redirecting to login...
                </div>
            `;

            setTimeout(() => {

                window.location.replace("/login");

            }, 1500);

        } else {

            const error = Array.isArray(data.detail)
                ? data.detail[0].msg
                : data.detail;

            message.innerHTML = `
                <div class="alert alert-danger">
                    ${error}
                </div>
            `;

        }

    } catch (error) {

        console.error(error);

        message.innerHTML = `
            <div class="alert alert-danger">
                Something went wrong.<br>
                Please try again.
            </div>
        `;

    } finally {

        button.disabled = false;
        button.innerHTML = "Register";

    }

});
function togglePassword(inputId, buttonId) {

    const input = document.getElementById(inputId);
    const button = document.getElementById(buttonId);

    button.addEventListener("click", () => {

        if (input.type === "password") {

            input.type = "text";

            button.innerHTML = "🙈";

        } else {

            input.type = "password";

            button.innerHTML = "👁";

        }

    });

}
togglePassword("password", "togglePassword");
togglePassword("confirmPassword", "toggleConfirmPassword");