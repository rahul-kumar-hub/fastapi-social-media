const postsContainer =
    document.getElementById("postsContainer");

async function loadPosts() {
    postsContainer.innerHTML = `
        <div class="text-center py-5">
            Loading stories...
        </div>
    `;
    try {
        const response = await fetch("/posts");
        const data = await response.json();
        renderPosts(data.items);
    }
    catch {
        postsContainer.innerHTML = `
        <div class="alert alert-danger">
            Unable to load stories.
        </div>
        `;
    }
}

function renderPosts(posts) {
    if (posts.length === 0) {
        postsContainer.innerHTML = `
        <div class="text-center py-5">
            <h4>No stories yet.</h4>
            <p>
                Be the first to publish.
            </p>
        </div>
        `;
        return;
    }
    postsContainer.innerHTML = "";
    posts.forEach(post => {
        postsContainer.innerHTML += createCard(post);
    });
}
loadPosts();
document.addEventListener("click", async (e) => {
    if (!e.target.classList.contains("save-post")) {
        return;
    }
    const button = e.target;
    const postId = button.dataset.id;
    button.disabled = true;
    try {
        const response = await fetch(
            `/posts/${postId}/save`,
            {
                method: "POST",
                credentials: "include",
            }
        );
        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }
        const data = await response.json();
        if (data.message === "Post saved") {
            button.innerHTML = "✅ Saved";
            button.classList.remove("btn-outline-primary");
            button.classList.add("btn-success");
        } else {
            button.innerHTML = "🔖 Save";
            button.classList.remove("btn-success");
            button.classList.add("btn-outline-primary");
        }
    } finally {
        button.disabled = false;
    }
});
function createCard(post) {
    return `
<div class="feed-card">
    <div class="feed-author">
        <img
            src="${post.author.image_path}"
            class="author-pic">
        <div>
            <strong>
                ${post.author.username}
            </strong>
            <br>
            <small>
                ${new Date(
        post.date_posted
    ).toLocaleDateString()}
            </small>
        </div>
    </div>
    <a
        href="/posts/blog/${post.id}"
        class="feed-title">
        ${post.title}
    </a>
    <p class="feed-preview">
        ${post.content.substring(0, 180)}...
    </p>
    <div class="feed-footer">
        <span>
            ❤️ ${post.like_count ?? 0}
        </span>
        <span>
            💬 ${post.comment_count ?? 0}
        </span>
        <button
            class="btn btn-sm btn-outline-primary save-post"
            data-id="${post.id}">
            🔖 Save
        </button>
        <a
            href="/posts/blog/${post.id}">
            Read More →
        </a>
    </div>
</div>
`;
}