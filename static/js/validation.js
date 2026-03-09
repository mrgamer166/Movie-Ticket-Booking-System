console.log("validation.js loaded");
document.addEventListener("DOMContentLoaded", function(){

    const registerForm = document.querySelector("form");

    if(registerForm){

        registerForm.addEventListener("submit", function(event){

            const password = document.querySelector("input[name='password']");
            const confirmPassword = document.querySelector("input[name='confirm_password']");

            if(confirmPassword && password.value !== confirmPassword.value){
                alert("Passwords do not match!");
                event.preventDefault();
            }

        });

    }

});