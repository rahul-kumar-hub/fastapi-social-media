const form = document.getElementById("createPostForm");
const button = form.querySelector("button");
const message = document.getElementById("message");

form.addEventListener("submit", async (e) => {

    e.preventDefault();

    message.innerHTML = "";

    button.disabled = true;
    button.innerText = "Publishing...";

    try {

        const response = await fetch("/posts", {

            method: "POST",

            credentials: "include",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                title: document.getElementById("title").value,
                content: document.getElementById("content").value

            })

        });

        if (!response.ok) {

            const error = await response.json();

            throw new Error(error.detail);

        }

        const post = await response.json();

        window.location.href = `/posts/blog/${post.id}`;

    } catch (error) {

        message.innerHTML =
            `<div class="alert alert-danger">${error.message}</div>`;

    } finally {

        button.disabled = false;
        button.innerText = "Publish";

    }

});