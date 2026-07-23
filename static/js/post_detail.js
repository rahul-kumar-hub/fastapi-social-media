const likeButton = document.getElementById("likeButton");
const likeText = document.getElementById("likeText");
const likeCount = document.getElementById("likeCount");

if (likeButton) {
    likeButton.addEventListener("click", async () => {
        const postId = window.location.pathname.split("/").pop();

        const response = await fetch(
            `/posts/${postId}/like`,
            {
                method: "POST",
                credentials: "include",
            }
        );
        if (!response.ok) {
            alert("Something went wrong.");
            return;
        }
        const data = await response.json();
        likeCount.innerText = data.like_count;
        if (data.message === "Post liked") {
            likeButton.classList.remove("btn-outline-danger");
            likeButton.classList.add("btn-danger");
            likeText.innerText = "Unlike";
        } else {
            likeButton.classList.remove("btn-danger");
            likeButton.classList.add("btn-outline-danger");
            likeText.innerText = "Like";
        }
    });
}

const postId = likeButton.dataset.postId;
const commentsContainer = document.getElementById("commentsContainer");
const commentInput = document.getElementById("commentInput");
const commentButton = document.getElementById("commentButton");

async function loadComments() {
    commentsContainer.innerHTML =
    `
    <div class="text-muted">
        Loading comments...
    </div>
    `;
    try {
        const response = await fetch(
            `/posts/${postId}/comments`
        );
        const comments = await response.json();
        renderComments(comments);
    }
    catch {
        commentsContainer.innerHTML =
        `
        <div class="alert alert-danger">
            Unable to load comments.
        </div>
        `;
    }
}
function renderComments(comments) {
    if (comments.length === 0) {
        commentsContainer.innerHTML =
        `
        <p class="text-muted">
            No comments yet.
        </p>
        `;
        return;
    }
    commentsContainer.innerHTML = "";
    comments.forEach(comment => {
        commentsContainer.innerHTML +=
        `
        <div class="card mt-3">
            <div class="card-body">
                <strong>
                    ${comment.author.username}
                </strong>
                <small class="text-muted ms-2">
                    ${new Date(comment.date_posted).toLocaleDateString()}
                </small>
                <p class="mt-2">
                    ${comment.content}
                </p>
            </div>
        </div>
        `;
    });
}
loadComments();

commentButton.addEventListener("click", postComment);
async function postComment() {
    const content = commentInput.value.trim();
    if (content === "") {
        alert("Please write a comment.");
        return;
    }
    try {
        const response = await fetch(
            `/posts/${postId}/comments`,
            {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    content: content
                })
            }
        );
        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }
        if (!response.ok) {
            alert("Unable to post comment.");
            return;
        }
        commentInput.value = "";
        loadComments();
    }
    catch (error) {
        console.error(error);
        alert("Server error.");
    }
}