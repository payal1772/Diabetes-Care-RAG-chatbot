async function readJsonResponse(response) {
    const text = await response.text();

    if (!text) {
        return {};
    }

    try {
        return JSON.parse(text);
    } catch (error) {
        throw new Error(`Backend returned a non-JSON response with status ${response.status}`);
    }
}

async function registerUser() {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const res = await fetch("/api/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name, email, password })
        });

        const data = await readJsonResponse(res);

        if (res.ok) {
            document.getElementById("authMessage").innerText = "Registration successful. Please login.";
            setTimeout(() => {
                window.location.href = "login.html";
            }, 1000);
        } else {
            document.getElementById("authMessage").innerText = data.error || "Registration failed";
        }
    } catch (error) {
        document.getElementById("authMessage").innerText = error instanceof TypeError
            ? "Could not connect to Flask. Make sure the backend server is running."
            : error.message;
    }
}

async function loginUser() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const res = await fetch("/api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        const data = await readJsonResponse(res);

        if (res.ok) {
            localStorage.setItem("token", data.token);
            localStorage.setItem("name", data.name);

            window.location.href = "chatbot.html";
        } else {
            document.getElementById("authMessage").innerText = data.error || "Login failed";
        }
    } catch (error) {
        document.getElementById("authMessage").innerText = error instanceof TypeError
            ? "Could not connect to Flask. Make sure the backend server is running."
            : error.message;
    }
}
