document
    .getElementById("task-form")
    .addEventListener("submit", async function (e) {
        e.preventDefault();
        const token = document.getElementById("token").value;
        const name = document.getElementById("name").value;
        const priority = document.getElementById("priority").value;
        const deadine = document.getElementById("deadine").value;
        const description = document.getElementById("description").value;


        const res = await fetch(`/api/receipt/task?token=${token}`{
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: name.value,
                priority: priority.value,
                deadline: deadline.value,
                description: description.value,
            })
        });

        const data = await res.json();

        var element = document.getElementById("result");
        element.classList.remove("result_fail")
        element.classList.remove("result_success")


    });