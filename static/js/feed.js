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

function renderPosts(posts){
    if(posts.length===0){
        postsContainer.innerHTML=`
        <div class="text-center py-5">
            <h4>No stories yet.</h4>
            <p>
                Be the first to publish.
            </p>
        </div>
        `;
        return;
    }
    postsContainer.innerHTML="";
    posts.forEach(post=>{
        postsContainer.innerHTML += createCard(post);
    });
}
loadPosts();

function createCard(post){
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
        ${post.content.substring(0,180)}...
    </p>
    <div class="feed-footer">
        <span>
            ❤️ ${post.like_count ?? 0}
        </span>
        <span>
            💬 ${post.comment_count ?? 0}
        </span>
        <a
            href="/posts/blog/${post.id}">
            Read More →
        </a>
    </div>
</div>
`;
}