// audit.js
function showAuditPopup() {
  const p = document.getElementById("auditSuccessPopup");
  p.classList.add("show");
  setTimeout(() => {
    window.location.href = "index.html";
  }, 3000);
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("contactForm");
  const successDiv = document.getElementById("formSuccess");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = {
      firstname: form.firstname.value.trim(),
      lastname: form.lastname.value.trim(),
      email: form.email.value.trim(),
      brandname: form.brandname.value.trim(),
      producturl: form.producturl.value.trim(),
      message: form.message.value.trim(),
    };

    // basic required fields check
    for (const k in formData) {
      if (!formData[k]) {
        alert("Please fill all required fields.");
        return;
      }
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/audit", {   // ✅ FIXED
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });

      if (res.ok) {
        if (successDiv) {
          successDiv.style.display = "block";
          successDiv.innerText =
            "Thanks — your audit request has been received. Our team will contact you soon.";
        }
        form.reset();
showAuditPopup();
return;

      }

      if (res.status === 409) {
        const j = await res.json().catch(()=>({}));
        alert(j.detail || "You already submitted a similar request recently.");
        return;
      }

      const j = await res.json().catch(()=>({}));
      alert(j.detail || "Failed to submit request. Try again later.");

    } catch (err) {
      console.error("Audit submit error:", err);
      alert("Network error. Please try again later.");
    }
  });
});


