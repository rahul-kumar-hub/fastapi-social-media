
let postPublished = false;
const form = document.getElementById("createPostForm");
const button = form.querySelector("button");
const title = document.getElementById("title");
const content = document.getElementById("content");
const message = document.getElementById("message");
const draftStatus =
    document.getElementById("draftStatus");
const titleCounter = document.getElementById("titleCount");
const charCount = document.getElementById("charCount");
const savedTitle = localStorage.getItem("draft_title");
const savedContent = localStorage.getItem("draft_content");
const coverImage = document.getElementById("coverImage");
const coverPreview = document.getElementById("coverPreview");

coverImage.addEventListener("change", () => {
    const file = coverImage.files[0];
    if (!file) {
        return;
    }
    coverPreview.src =
        URL.createObjectURL(file);
    coverPreview.classList.remove("d-none");
});

if (savedTitle) {
    title.value = savedTitle;
}
if (savedContent) {
    content.value = savedContent;
}
titleCounter.innerText = title.value.length;

charCount.innerText =
    `${content.value.length} characters`;

content.style.height = "auto";
content.style.height =
    content.scrollHeight + "px";
title.addEventListener("input", () => {
    localStorage.setItem(
        "draft_title",
        title.value
    );
    draftStatus.innerText = "Saving...";
    setTimeout(() => {

        draftStatus.innerText = "Draft Saved";

    }, 500);
});
content.addEventListener("input", () => {
    localStorage.setItem(
        "draft_content",
        content.value
    );
    draftStatus.innerText = "Saving...";

    setTimeout(() => {

        draftStatus.innerText = "Draft Saved";

    }, 500);
});

title.addEventListener("input", () => {
    titleCounter.innerText = title.value.length;
});
content.addEventListener("input", () => {
    content.style.height = "auto";
    content.style.height = content.scrollHeight + "px";
    charCount.innerText =
        `${content.value.length} characters`;
});
form.addEventListener("submit", async (e) => {

    e.preventDefault();

    message.innerHTML = "";
    if (title.value.trim() === "") {
        message.innerHTML = `
        <div class="alert alert-danger">
            Please enter a title.
        </div>
    `;
        title.focus();
        return;
    }
    if (content.value.trim() === "") {
        message.innerHTML = `
        <div class="alert alert-danger">
            Please write something.
        </div>
    `;

        content.focus();

        return;

    }
    button.disabled = true;
    button.innerHTML = `
<span class="spinner-border spinner-border-sm"></span>
 Publishing...
`;

    try {
        const formData = new FormData();

        formData.append(
            "title",
            title.value
        );

        formData.append(
            "content",
            content.value
        );

        if (coverImage.files.length > 0) {

            formData.append(
                "cover_image",
                coverImage.files[0]
            );

        }
        const response = await fetch(
            "/posts",
            {
                method: "POST",
                credentials: "include",
                body: formData,
            }
        );
        if (response.ok) {
            postPublished = true;
            const post = await response.json();
            localStorage.removeItem("draft_title");
            localStorage.removeItem("draft_content");
            window.location.href = `/posts/blog/${post.id}`;
        } else {
            const error = await response.json();
            console.log(error);
            message.innerHTML = `
        <div class="alert alert-danger">
            ${error.detail}
        </div>
        `;
            button.disabled = false;
            button.innerText = "Publish Story";
        }
    } catch (error) {
        console.error(error);
        message.innerHTML = `
    <div class="alert alert-danger">
        Unable to connect to the server.
    </div>
    `;
        button.disabled = false;
        button.innerText = "Publish Story";
    }

});
document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "Enter") {
        form.requestSubmit();
    }
});

window.addEventListener("beforeunload", function (e) {

    if (postPublished) return;

    if (
        title.value.trim() ||
        content.value.trim()
    ) {

        e.preventDefault();
        e.returnValue = "";

    }

});