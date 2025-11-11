// backend/JS/contact.js
document.addEventListener("DOMContentLoaded", () => {
  // find the contact form - match your HTML which uses class "contact-form"
  const form = document.querySelector(".contact-form");
  if (!form) return;

  // create a small success div if not present
  let successDiv = document.getElementById("contact-success");
  if (!successDiv) {
    successDiv = document.createElement("div");
    successDiv.id = "contact-success";
    successDiv.style.display = "none";
    successDiv.style.padding = "12px";
    successDiv.style.background = "Black";
    successDiv.style.border = "1px solid #b7f0c5";
    successDiv.style.margin = "10px 0";
    form.parentNode.insertBefore(successDiv, form.nextSibling);
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // grab inputs (your HTML uses plain inputs without names in the example; adapt selectors if needed)
    const firstnameInput = form.querySelector('input[type="text"]') || form.querySelector('input[name="firstname"]') || null;
    const emailInput = form.querySelector('input[type="email"]') || form.querySelector('input[name="email"]') || null;
    const subjectInput = form.querySelector('input[placeholder*="Subject"]') || form.querySelector('input[name="subject"]') || null;
    const messageInput = form.querySelector('textarea') || form.querySelector('textarea[name="message"]') || null;

    const firstname = firstnameInput ? firstnameInput.value.trim() : "";
    const email = emailInput ? emailInput.value.trim() : "";
    const subject = subjectInput ? subjectInput.value.trim() : "";
    const message = messageInput ? messageInput.value.trim() : "";

    if (!firstname || !email || !subject || !message) {
      alert("Please fill all required fields.");
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/contact",{
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ firstname, email, subject, message })
      });

      if (res.ok) {
        // show inline success message
        successDiv.innerText = "Thanks — your message has been sent. Our team will contact you soon.";
        successDiv.style.display = "block";
        form.reset();

        // hide after some seconds then redirect to index (remove redirect if you don't want it)
        setTimeout(() => {
          successDiv.style.display = "none";
          // redirect to homepage (same-origin)
          // window.location.href = "/index.html";
        }, 3500);

        return;
      }

      if (res.status === 409) {
        const j = await res.json().catch(()=>({}));
        alert(j.detail || "Duplicate request recently. Please try later.");
        return;
      }

      // other failure
      const j = await res.json().catch(()=>({}));
      alert(j.detail || "Failed to submit contact request. Try again later.");

    } catch (err) {
      console.error("Contact submit error:", err);
      alert("Network error. Please try again.");
    }
  });
});
