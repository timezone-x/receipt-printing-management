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
        } else {
            element.classList.add("result_fail")
            if (data.status == 401) {
                element.innerHTML = "Task Failed to send<br> 401: Invalid Token."
            } else {
                element.innerHTML = "Task Failed to send<br> 403: Invalid Permission."
            }
        }

    });