const form = document.getElementById("editPostForm");
const title = document.getElementById("title");
const content = document.getElementById("content");
const message = document.getElementById("message");
const button = form.querySelector("button");
// Current URL:
// /posts/edit/7
const postId = window.location.pathname.split("/").pop();
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    button.disabled = true;
    button.innerHTML = "Updating...";
    try {
        const response = await fetch(`/posts/${postId}`, {
            method: "PATCH",
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                title: title.value,
                content: content.value
            })
        });
        const data = await response.json();
        if (response.ok) {
            message.innerHTML = `
                <div class="alert alert-success">
                    Story updated successfully.
                </div>
            `;
            setTimeout(() => {
                window.location.href =
                    `/posts/blog/${postId}`;
            }, 1000);
        }
        else {
            message.innerHTML = `
                <div class="alert alert-danger">
                    ${data.detail}
                </div>
            `;
        }
    }
    catch {
        message.innerHTML = `
            <div class="alert alert-danger">
                Server Error
            </div>
        `;
    }
    button.disabled = false;
    button.innerHTML = "Update Story";

});