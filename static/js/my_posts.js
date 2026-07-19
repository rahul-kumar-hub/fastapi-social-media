const deleteButtons =
    document.querySelectorAll(".delete-post");

deleteButtons.forEach((button) => {

    button.addEventListener("click", async () => {

        const postId = button.dataset.id;

        const confirmed = confirm(
            "Are you sure you want to delete this post?"
        );

        if (!confirmed) {
            return;
        }

        try {

            const response = await fetch(
                `/posts/${postId}`,
                {
                    method: "DELETE",
                    credentials: "include",
                }
            );

            if (response.ok) {

                document
                    .getElementById(`post-${postId}`)
                    .remove();

            } else {

                alert("Unable to delete post.");

            }

        } catch {

            alert("Server error.");

        }

    });

});