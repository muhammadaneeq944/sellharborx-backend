// login.js
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("login_form"); // ✅ matches your HTML

  if (!form) {
    console.error("Form with id='login_form' not found.");
    return;
  }

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim(); // ✅ fixed ID here

    if (!email || !password) {
      alert("Please fill in both fields.");
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json().catch(() => ({}));

      console.log("Response:", data); // helpful for debugging

      if (data.success) {
        alert(data.message || "Login successful!");
        localStorage.setItem("shx_welcome_username", data.username || "");
        window.location.href = "index.html"; // ✅ redirect on success
      } else {
        alert(data.message || "Invalid credentials. Please try again.");
      }
    } catch (err) {
      console.error("Login error:", err);
      alert("Server error. Please check your connection.");
    }
  });
});
