const profileForm = document.getElementById("profileForm");

profileForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username =
        document.getElementById("username").value;
    const email =
        document.getElementById("email").value;

    try {
        const response = await fetch(
            "/users/me",
            {
                method: "PATCH",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username,
                    email
                })
            }
        );
        const data = await response.json();
        if (response.ok) {
            document.getElementById("message").innerHTML = `
            <div class="alert alert-success">
                Profile updated successfully.
            </div>
            `;
        } else {
            document.getElementById("message").innerHTML = `
            <div class="alert alert-danger">
                ${data.detail}
            </div>
            `;
        }
    } catch {
        alert("Unable to connect to server.");
    }
});
const passwordForm = document.getElementById("passwordForm");
passwordForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const currentPassword =
        document.getElementById("currentPassword").value;
    const newPassword =
        document.getElementById("newPassword").value;
    const confirmPassword =
        document.getElementById("confirmPassword").value;
    if (newPassword !== confirmPassword) {
        document.getElementById("message").innerHTML = `
            <div class="alert alert-danger">
                Passwords do not match.
            </div>
        `;
        return;
    }
    try {
        const response = await fetch(
            "/users/change-password",
            {
                method: "PATCH",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            }
        );
        const data = await response.json();
        if (response.ok) {
            document.getElementById("message").innerHTML = `
                <div class="alert alert-success">
                    Password changed successfully.
                </div>
            `;
            passwordForm.reset();
        } else {
            document.getElementById("message").innerHTML = `
                <div class="alert alert-danger">
                    ${data.detail}
                </div>
            `;
        }
    } catch {
        document.getElementById("message").innerHTML = `
            <div class="alert alert-danger">
                Server Error.
            </div>
        `;
    }
});

const pictureForm = document.getElementById("pictureForm");
pictureForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput =
        document.getElementById("picture");
    if (fileInput.files.length === 0) {
        document.getElementById("message").innerHTML = `
            <div class="alert alert-warning">
                Please choose an image.
            </div>
        `;
        return;
    }
    const formData = new FormData();
    formData.append(
        "file",
        fileInput.files[0]
    );
    try {
        const response = await fetch(
            "/users/me/picture",
            {
                method: "PATCH",
                credentials: "include",
                body: formData
            }
        );
        const data = await response.json();
        if (response.ok) {
            document.getElementById("profileImage").src =
                data.image_path + "?t=" + Date.now();
            document.getElementById("message").innerHTML = `
                <div class="alert alert-success">
                    Profile picture updated successfully.
                </div>
            `;
            pictureForm.reset();
        } else {
            document.getElementById("message").innerHTML = `
                <div class="alert alert-danger">
                    ${data.detail}
                </div>
            `;
        }
    } catch {
        document.getElementById("message").innerHTML = `
            <div class="alert alert-danger">
                Upload failed.
            </div>
        `;
    }
});

const deletePictureBtn = document.getElementById("deletePicture");

deletePictureBtn.addEventListener("click", async () => {
    if (!confirm("Are you sure you want to remove your profile picture?")) {
        return;
    }
    try {
        const response = await fetch(
            "/users/me/picture",
            {
                method: "DELETE",
                credentials: "include",
            }
        );
        const data = await response.json();
        if (response.ok) {
            document.getElementById("profileImage").src =
                data.image_path + "?t=" + Date.now();
            document.getElementById("message").innerHTML = `
                <div class="alert alert-success">
                    Profile picture removed successfully.
                </div>
            `;
        } else {
            document.getElementById("message").innerHTML = `
                <div class="alert alert-danger">
                    ${data.detail}
                </div>
            `;
        }
    } catch {
        document.getElementById("message").innerHTML = `
            <div class="alert alert-danger">
                Server Error.
            </div>
        `;
    }
});

const deleteAccountBtn = document.getElementById("deleteAccount");

deleteAccountBtn.addEventListener("click", async () => {
    const password =
        document.getElementById("deletePassword").value;
    if (password.trim() === "") {
        document.getElementById("message").innerHTML = `
            <div class="alert alert-danger">
                Please enter your password.
            </div>
        `;

        return;
    }
    const confirmDelete = confirm(
        "This will permanently delete your account.\n\nAre you sure?"
    );
    if (!confirmDelete) {
        return;
    }
    try {
        const response = await fetch(
            "/users/me",
            {
                method: "DELETE",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    password: password
                })
            }
        );
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }
        const data = await response.json();
        document.getElementById("message").innerHTML = `
            <div class="alert alert-danger">
                ${data.detail}
            </div>
        `;
    } catch {
        document.getElementById("message").innerHTML = `
            <div class="alert alert-danger">
                Server Error.
            </div>
        `;
    }
});