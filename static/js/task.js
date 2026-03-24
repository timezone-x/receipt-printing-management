function fillKeySlot() {
    console.log("Checking for saved key")
    const token = localStorage.getItem("auth_key")
    if (token) {
        console.log("Found Key!")
        document.getElementById("token").value = token;
        const checkBox = document.getElementById("remember_me");
        checkBox.checked = true;

    }
}

fillKeySlot();



document
    .getElementById("task-form")
    .addEventListener("submit", async function (e) {
        e.preventDefault();
        console.log("loading task data")
        const token = document.getElementById("token").value;
        const name = document.getElementById("name").value;
        const priority = document.querySelector('input[name="priority"]:checked')?.value;
        const deadline = document.getElementById("deadline").value;
        const description = document.getElementById("description").value;
        const remember_me = document.getElementById("remember_me").checked;

        console.log("sending task data")
        const res = await fetch(`/api/receipt/task?token=${token}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: name,
                priority: priority,
                deadline: deadline,
                description: description,
            })
        });

        const data = await res.json();

        var element = document.getElementById("result");
        element.classList.remove("result_fail")
        element.classList.remove("result_success")
        if (data.status == 200) {
            element.classList.add("result_success")
            element.textContent = "Task Sent!"
            document.getElementById("task-form").reset();
            if (remember_me) {
                console.log("Saving Key!")
                localStorage.setItem("auth_key", token);
                fillKeySlot();
            } else {
                console.log("Clearing auth_key")
                localStorage.removeItem("auth_key");
            }
        } else {
            element.classList.add("result_fail")
            if (data.status == 401) {
                element.innerHTML = "Task Failed to send<br> 401: Invalid Token."
            } else {
                element.innerHTML = "Task Failed to send<br> 403: Invalid Permission."
            }
        }

    });