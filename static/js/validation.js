console.log("JS LOADED ✅");

document.addEventListener("DOMContentLoaded", function () {

    /* ================= REGISTER PAGE ================= */

    const registerForm = document.querySelector("form");
    const usernameInput = document.querySelector("#username");
    const usernameStatus = document.querySelector("#username-status");
    const submitBtn = document.querySelector("button[type='submit']");

    // Only run on register page
    if (registerForm && usernameInput && usernameStatus) {

        submitBtn.disabled = true;

        usernameInput.addEventListener("input", function () {

            const username = usernameInput.value;

            if (username.length < 3) {
                usernameStatus.textContent = "Minimum 3 characters required";
                usernameStatus.style.color = "gray";
                submitBtn.disabled = true;
                return;
            }

            usernameStatus.textContent = "Checking...";
            usernameStatus.style.color = "gray";

            fetch(`/check-username?username=${username}`)
                .then(res => res.json())
                .then(data => {

                    if (data.available) {
                        usernameStatus.textContent = "Username available";
                        usernameStatus.style.color = "green";
                        submitBtn.disabled = false;
                    } else {
                        usernameStatus.textContent = "Username already taken";
                        usernameStatus.style.color = "red";
                        submitBtn.disabled = true;
                    }

                })
                .catch(() => {
                    usernameStatus.textContent = "Error checking username";
                    usernameStatus.style.color = "red";
                    submitBtn.disabled = true;
                });

        });

        registerForm.addEventListener("submit", function (e) {

            const password = document.querySelector("input[name='password']");
            const confirmPassword = document.querySelector("input[name='confirm_password']");

            if (password.value.length < 8) {
                alert("Password must be at least 8 characters");
                e.preventDefault();
                return;
            }

            if (password.value !== confirmPassword.value) {
                alert("Passwords do not match");
                e.preventDefault();
            }

        });
    }

    /* ================= SEAT BOOKING ================= */

    window.selectSeat = function (btn) {

        document.querySelectorAll(".seat").forEach(s => {
            s.classList.remove("selected");
        });

        btn.classList.add("selected");

        const seat = btn.innerText;

        document.getElementById("selected-seat").value = seat;
        document.getElementById("selected-text").innerText =
            "Selected Seat: " + seat;
    };

});