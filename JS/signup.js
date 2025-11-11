// signup.js
document.getElementById("sign_up").addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("Username").value.trim();
    const email = document.getElementById("signupEmail").value.trim();
    const password = document.getElementById("password").value;
    const confirmPass = document.getElementById("ConfirmPassword").value;

    // Basic validations (frontend)
    if (!username || !email || !password || !confirmPass) {
        alert("Please fill all fields.");
        return;
    }

    if (password !== confirmPass) {
        alert("Passwords do not match.");
        return;
    }

    const payload = {
        username,
        email,
        password,
        confirmPassword: confirmPass
    };

    try {
        const res = await fetch("http://127.0.0.1:8000/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            // If server returns non-2xx, try to get error message
            const err = await res.json().catch(() => null);
            const msg = err && err.detail ? err.detail : "Signup failed.";
            alert(msg);
            return;
        }

        const data = await res.json();

        if (data.alreadyExists) {
            // Existing user -> redirect to login page
            window.location.href = "my-account.html";
            return;
        }

        if (data.success) {
            showBigPopup();
            return;
        }


        // Fallback
        alert(data.message || "Unexpected response from server.");
    } catch (error) {
        console.error("Network or server error:", error);
        alert("Could not reach server. Make sure backend is running at http://127.0.0.1:8000");
    }
});

function showToast(msg){
    const t = document.getElementById("toast");
    t.textContent = msg;
    t.classList.add("show");
    setTimeout(()=> t.classList.remove("show"), 3000);
}

function showBigPopup() {
  const p = document.getElementById("bigSuccessPopup");
  p.classList.add("show");
  setTimeout(() => {
    window.location.href = "index.html";
  }, 3000);
}

