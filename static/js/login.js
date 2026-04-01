document
.getElementById('login-form')
.addEventListener('submit', async function (e) {
    e.preventDefault()
    console.log("attempting to login")
    const userId = document.getElementById("user-id").value
    const password = document.getElementById("password").value

    const res = await fetch("/api/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: Json.stringify({
            user_id: userId,
            password:password,
        })
    });

    const data = await res.json();
    var element = document.getElementById("result");
    element.classList.remove("result_fail")
    if (data.status == 401) {
        consol.log("failed to login: Invalid user id or password")
        element.classList.add("result_fail")
        element.textContent = "Invalid user Id or password."
    }
})