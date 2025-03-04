

async function signup() {
    const mobile_phone = document.getElementById("signup-phone").value;
    const name = document.getElementById("signup-name").value;
    const password = document.getElementById("signup-password").value;

    const response = await fetch("http://localhost:8000/signup/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mobile_phone, name, password })
    });

    const data = await response.json();
    alert(data.message);
    if (response.ok) window.location.href = "login.html";
}

async function login() {
    const mobile_phone = document.getElementById("login-phone").value;
    const password = document.getElementById("login-password").value;

    const response = await fetch("http://localhost:8000/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mobile_phone, password })
    });

    const data = await response.json();
    if (response.ok) {
        sessionStorage.setItem("token", data.access_token);
        window.location.href = "index.html";
    } else {
        alert("Login failed: " + data.detail);
    }
}

async function transcribeVideo() {
    const video_url = document.getElementById("video-url").value;
    const token = sessionStorage.getItem("token");

    const response = await fetch("http://localhost:8000/transcribe/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ url: video_url })
    });

    if (response.status === 401) {
        alert("Session expired. Please log in again.");
        logout();
        return;
    }

    const data = await response.json();
    document.getElementById("transcription-status").textContent = data.status;
}


async function askQuestion(video_url, question) {
    try {
        const token = sessionStorage.getItem("token");

        // Check if token exists
        if (!token) {
            alert("You must be logged in to ask a question. Redirecting to login...");
            window.location.href = "login.html";
            return;
        }

        // Send the question and video URL to the server
        const response = await fetch("http://127.0.0.1:8000/ask/", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": `Bearer ${token}` // Include the token for authenticated requests
            },
            body: JSON.stringify({ url: video_url, question }) // Send both video URL and question
        });

        // Handle different response statuses
        if (response.status === 401) {
            alert("Session expired or invalid token. Please log in again.");
            logout();
            return;
        }

        if (response.status === 404) {
            const errorData = await response.json();
            alert(errorData.detail || "Video not found or you don't have access to it.");
            return;
        }

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Response:", data);
        
        // Display the answer
        document.getElementById("answer").innerText = data.answer;

        // Immediately fetch and display the updated chat history
        await fetchChatHistory();
    } catch (error) {
        console.error("Error asking question:", error);
        alert(`Failed to get answer: ${error.message}`);
    }
}

function handleAskQuestion() {
    const video_url = document.getElementById("video_url").value.trim();
    const question = document.getElementById("question").value.trim();

    if (!video_url || !question) {
        alert("Please enter both a video URL and a question.");
        return;
    }

    askQuestion(video_url, question);
}

async function fetchChatHistory() {
    try {
        const token = sessionStorage.getItem("token");

        if (!token) {
            alert("You must be logged in to view chat history.");
            return;
        }

        // Fetch the latest chat history from the server
        const response = await fetch("http://localhost:8000/chathistory/", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        });

        if (response.status === 401) {
            alert("Session expired. Please log in again.");
            logout();
            return;
        }

        const history = await response.json();
        const chatHistoryList = document.getElementById("chat-history");

        // Clear existing chat history
        chatHistoryList.innerHTML = "";

        if (history.length === 0) {
            chatHistoryList.innerHTML = "<li>No chat history found.</li>";
            return;
        }

        // Append new chat history entries
        history.forEach(entry => {
            const li = document.createElement("li");
            li.textContent = `Q: ${entry.question} - A: ${entry.answer}`;
            chatHistoryList.appendChild(li);
        });
    } catch (error) {
        console.error("Error fetching chat history:", error);
    }
}
function checkSession() {
    const token = sessionStorage.getItem("token");

    if (!token) {
        console.log("No token found. User is not logged in.");
        return; // Allow user to log in manually instead of immediately logging out
    }

    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        if (!payload.exp) {
            console.error("JWT token does not have an 'exp' field!");
            alert("Invalid session. Please log in again.");
            logout();
            return;
        }
        const exp = payload.exp * 1000;
        const currentTime = Date.now();
        const timeRemaining = exp - currentTime;


        console.log(`Token Expiry Time: ${new Date(exp).toLocaleString()}`);
        console.log(`Current Time: ${new Date(currentTime).toLocaleString()}`);
        console.log(`Time Until Expiration: ${timeRemaining / 1000} seconds`);

        if (timeRemaining <= 0) {
            alert("Session expired. Please log in again.");
            logout();
        } else {
            setTimeout(() => {
                alert("Session expired. Please log in again.");
                logout();
            }, timeRemaining);
        }
    } catch (error) {
        console.error("Error decoding token:", error);
        alert("Session expired. Please log in again.");
        logout();
    }
}





// ✅ Logout function
async function logout() {
    const token = sessionStorage.getItem("token");

    if (token) {
        try {
            // Call the logout endpoint to invalidate the token
            await fetch("http://localhost:8000/logout/", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            });
        } catch (error) {
            console.error("Error during logout:", error);
        }
    }

    // Clear the token from sessionStorage
    sessionStorage.removeItem("token");

    // Redirect to the login page
    window.location.href = "login.html";
}

// Add event listener for the logout button
document.addEventListener("DOMContentLoaded", function () {
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", logout);
    }
});




