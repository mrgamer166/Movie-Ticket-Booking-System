console.log("JS WORKING");

document.addEventListener("DOMContentLoaded", function(){

    const registerForm = document.querySelector("form");
    const usernameInput = document.querySelector("#username");
    const usernameStatus = document.querySelector("#username-status");
    const submitBtn = document.querySelector("button[type='submit']");

    if(submitBtn){
        submitBtn.disabled = true;
    }

    if(registerForm){
        registerForm.addEventListener("submit", function(event){

            const password = document.querySelector("input[name='password']");
            const confirmPassword = document.querySelector("input[name='confirm_password']");

            if(password.value.length < 8){
                alert("Password must be at least 8 characters long");
                event.preventDefault();
                return;
            }

            if(password.value !== confirmPassword.value){
                alert("Passwords do not match");
                event.preventDefault();
            }

        });
    }

    if(usernameInput){

        usernameInput.addEventListener("keyup", function(){

            const username = usernameInput.value;

            if(username.length < 3){
                usernameStatus.textContent = "Minimum 3 characters required";
                usernameStatus.style.color = "gray";
                submitBtn.disabled = true;
                return;
            }

            usernameStatus.textContent = "Checking...";
            usernameStatus.style.color = "gray";

            fetch(`/check-username?username=${username}`)
            .then(response => response.json())
            .then(data => {

                if(data.available){
                    usernameStatus.textContent = "Username available";
                    usernameStatus.style.color = "green";
                    submitBtn.disabled = false;
                }else{
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

    }
    let selectedSeat = null;

    function selectSeat(btn){

        // remove previous selection
        document.querySelectorAll(".seat").forEach(s => {
            s.classList.remove("selected");
        });

        btn.classList.add("selected");

        selectedSeat = btn.innerText;

        document.getElementById("selected-seat").value = selectedSeat;
        document.getElementById("selected-text").innerText =
            "Selected Seat: " + selectedSeat;
    }

});