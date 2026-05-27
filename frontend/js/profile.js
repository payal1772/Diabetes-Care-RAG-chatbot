function getStoredToken() {
    const token = localStorage.getItem("token");

    if (!token || token === "undefined" || token === "null" || token.split(".").length !== 3) {
        localStorage.removeItem("token");
        localStorage.removeItem("name");
        return null;
    }

    return token;
}

function requireLogin() {
    window.location.href = "login.html";
}

const token = getStoredToken();

if (!token) {
    window.location.href = "login.html";
}

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

async function loadProfile() {
    const message = document.getElementById("profileMessage");

    try {
        const res = await fetch("/api/profile", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await readJsonResponse(res);

        if (res.status === 401) {
            localStorage.removeItem("token");
            localStorage.removeItem("name");
            requireLogin();
            return;
        }

        if (!res.ok) {
            throw new Error(data.error || "Profile request failed");
        }

        document.getElementById("name").innerText = data.name || "--";
        document.getElementById("email").innerText = data.email || "--";
        document.getElementById("totalLogs").innerText = data.total_logs ?? 0;
        document.getElementById("avgGlucose").innerText = data.average_glucose ?? 0;
        document.getElementById("profileInitial").innerText = (data.name || "U").trim().slice(0, 1).toUpperCase();

        message.innerText = "Profile loaded";
        message.classList.add("is-success");
    } catch (error) {
        message.innerText = "Could not load profile. Please try signing in again.";
        message.classList.add("is-error");
    }
}

if (token) {
    loadProfile();
}
