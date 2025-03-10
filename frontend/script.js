async function signup() {
    const mobile_phone = document.getElementById("signup-phone").value;
    const name = document.getElementById("signup-name").value;
    const password = document.getElementById("signup-password").value;

    // Validate mobile number length
    if (mobile_phone.length !== 10) {
        alert("Please enter a 10-digit mobile number.");
        return; // Stop execution if validation fails
    }

    try {
        const response = await fetch("http://127.0.0.1:8001/signup/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mobile_phone, name, password })
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message); // Success message from the server
            window.location.href = "login.html"; // Redirect to login page
        } else {
            // Handle specific error cases
            if (response.status === 400 && data.detail === "Mobile number already registered") {
                alert("You're already signed up. Redirecting to the login page...");
                window.location.href = "login.html"; // Redirect to login page
            } else {
                alert("Signup failed: " + (data.detail || "Unknown error")); // Show error message
            }
        }
    } catch (error) {
        console.error("Error during signup:", error);
        alert("An error occurred during signup. Please try again.");
    }
}

async function login() {
    const mobile_phone = document.getElementById("login-phone").value;
    const password = document.getElementById("login-password").value;

    // Validate mobile number length
    if (mobile_phone.length !== 10) {
        alert("Please enter a 10-digit mobile number.");
        return; // Stop execution if validation fails
    }

    const response = await fetch("http://127.0.0.1:8001/login/", {
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

async function transcribeAudioFile() {
    const fileInput = document.getElementById("audio-file");
    const file = fileInput.files[0];
    const token = sessionStorage.getItem("token");

    if (!file) {
        alert("Please select an audio file.");
        return;
    }

    // Show loading indicator
    const transcriptionStatus = document.getElementById("transcription-status");
    if (!transcriptionStatus) {
        console.error("transcription-status element not found!");
        return;
    }
    transcriptionStatus.textContent = "⏳ Transcribing audio... Please wait.";
    transcriptionStatus.style.color = "blue";

    const formData = new FormData();
    formData.append("audio", file);

    try {
        const response = await fetch("http://127.0.0.1:8001/transcribe/audio/", {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` },
            body: formData
        });

        console.log("Response status:", response.status); // Log the response status
        console.log("Response headers:", response.headers); // Log the response headers

        // Handle token expiration (401 Unauthorized)
        if (response.status === 401) {
            alert("Your session has expired. Please log in again.");
            logout(); // Call the logout function to clear the token and redirect to the login page
            return;
        }

        if (response.ok) {
            const data = await response.json();
            console.log("Server Response Data:", data); // Log the full response data

            const audioTranscription = document.getElementById("audio-transcription");
            if (!audioTranscription) {
                console.error("audio-transcription element not found!");
                return;
            }
            audioTranscription.textContent = data.transcription;

            transcriptionStatus.textContent = "✅ Transcription Completed!";
            transcriptionStatus.style.color = "green";
        } else {
            console.error("Server Response Error:", response.status, response.statusText);
            throw new Error("Failed to transcribe audio.");
        }
    } catch (error) {
        console.error("Error transcribing audio:", error);
        transcriptionStatus.textContent = "❌ Failed to transcribe audio. Please try again.";
        transcriptionStatus.style.color = "red";
    }
}

async function askQuestion(question) {
    try {
        const token = sessionStorage.getItem("token");

        // Check if token exists
        if (!token) {
            alert("You must be logged in to ask a question. Redirecting to login...");
            window.location.href = "login.html";
            return;
        }

        // Send the question to the server
        const response = await fetch("http://127.0.0.1:8001/ask/", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": `Bearer ${token}` // Include the token for authenticated requests
            },
            body: JSON.stringify({ question }) // Send only the question
        });

        // Handle different response statuses
        if (response.status === 401) {
            alert("Session expired or invalid token. Please log in again.");
            logout();
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
    const question = document.getElementById("question").value.trim();

    if (!question) {
        alert("Please enter a question.");
        return;
    }

    askQuestion(question);
}

async function fetchChatHistory() {
    try {
        const token = sessionStorage.getItem("token");

        if (!token) {
            alert("You must be logged in to view chat history.");
            return;
        }

        // Fetch the latest chat history from the server
        const response = await fetch("http://127.0.0.1:8001/chathistory/", {
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
            await fetch("http://127.0.0.1:8001/logout/", {
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