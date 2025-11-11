// backend/JS/newsletter.js
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".newsletter-form");
  if (!form) return;

  const input = form.querySelector('input[name="email"]') || form.querySelector('input[type="email"]');
  // small inline success box
  let successDiv = document.getElementById("newsletter-success");
  if (!successDiv) {
    successDiv = document.createElement("div");
    successDiv.id = "newsletter-success";
    successDiv.style.display = "none";
    successDiv.style.padding = "12px";
    successDiv.style.background = "black";
   
    successDiv.style.margin = "10px 0";
    form.parentNode.insertBefore(successDiv, form.nextSibling);
  }

  const API_BASE = "http://127.0.0.1:8000"; // change in production

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = (input && input.value || "").trim();
    if (!email) { alert("Please enter your email."); return; }

    try {
      const res = await fetch(API_BASE + "/newsletter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email })
      });

      if (res.status === 201 || res.ok) {
        successDiv.innerText = "Thanks — you are subscribed. Our team will contact you soon.";
        successDiv.style.display = "block";
        form.reset();
        // hide after a few seconds
        setTimeout(() => { successDiv.style.display = "none"; }, 5000);
        return;
      }

      if (res.status === 409) {
        // duplicate
        const j = await res.json().catch(()=>({}));
        alert(j.detail || "You are already subscribed.");
        return;
      }

      const j = await res.json().catch(()=>({}));
      alert(j.detail || "Failed to subscribe. Try again later.");

    } catch (err) {
      console.error("Newsletter error:", err);
      alert("Network error. Please try again.");
    }
  });
});
