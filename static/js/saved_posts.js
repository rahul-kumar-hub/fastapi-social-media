document.addEventListener("click", async (e) => {

    if (!e.target.classList.contains("remove-saved")) {
        return;
    }

    if (!confirm("Remove this post from Saved?")) {
        return;
    }

    const button = e.target;
    const postId = button.dataset.id;

    const response = await fetch(
        `/posts/${postId}/save`,
        {
            method: "POST",
            credentials: "include",
        }
    );

    if (!response.ok) {
        alert("Unable to remove.");
        return;
    }

    // Remove the card from the page
    button.closest(".card").remove();

});