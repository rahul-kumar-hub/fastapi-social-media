const form = document.getElementById("loginForm");

form.addEventListener("submit", async function (e) {

    e.preventDefault();

    const formData = new FormData(form);

    const response = await fetch("/users/login", {

        method: "POST",

        body: formData,

        credentials: "include"

    });

    if (response.ok) {

        window.location.replace("/feed");

    } else {

        document.getElementById("errorMessage").innerText =
            "Invalid email or password.";

    }

});