// // ✅ Get selected package from URL
// const params = new URLSearchParams(window.location.search);
// const pkg = params.get("package") || "Not Selected";
// const price = params.get("price") || "Custom";

// // Update UI
// document.getElementById("pkg-name").innerText = "Selected Package: " + pkg;
// document.getElementById("pkg-price").innerText = "Price: $" + price;

// // ✅ Handle Form Submission
// document.getElementById("packageForm").addEventListener("submit", async (e) => {
//   e.preventDefault();

//   const data = {
//     package: pkg,
//     price,
//     name: document.getElementById("name").value.trim(),
//     email: document.getElementById("email").value.trim(),
//     company: document.getElementById("company").value.trim(),
//     product: document.getElementById("product").value.trim(),
//     url: document.getElementById("url").value.trim(),
//     businessType: document.getElementById("business-type").value,
//     notes: document.getElementById("notes").value.trim()
//   };

//   try {
//     const res = await fetch("http://127.0.0.1:8000/choose-package", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify(data)
//     });

//     if (res.ok) {
//       localStorage.setItem("pkg_flash", "Thank you! Your package details were submitted successfully.");
//       window.location.href = "/index.html";
//     } else {
//       const err = await res.json();
//       alert(err.detail || "Submission failed. Try again.");
//     }
//   } catch (err) {
//     console.error("Network error:", err);
//     alert("Network error. Please try again later.");
//   }
// });

// backend/JS/package-form.js



// backend/JS/package-form.js

// backend/JS/package-form.js

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("packageForm");
  const pkgNameEl = document.getElementById("pkg-name");
  const pkgPriceEl = document.getElementById("pkg-price");

  // ✅ Get selected package and price from URL
  const params = new URLSearchParams(window.location.search);
  const pkg = params.get("package") || "Not Selected";
  const price = params.get("price") || "Custom";

  // ✅ Update visible package summary
  pkgNameEl.textContent = `Selected Package: ${pkg}`;
  pkgPriceEl.textContent = `Price: ${price.startsWith("$") ? price : "$" + price}`;

  // ✅ Backend API endpoint (FastAPI)
  const API_URL = "http://127.0.0.1:8000/choose-package";

  // ✅ Create popup dynamically (hidden initially)
  const popupHTML = `
    <div id="package-popup" class="popup-overlay">
      <div class="popup-modal">
        <h2>🎉 Request Submitted Successfully!</h2>
        <p>Thank you for choosing <b>Sell Harbor X</b>.</p>
        <p>We’ve received your <b>${pkg}</b> request and will contact you within 24 hours.</p>
        <p>A confirmation email has also been sent to your provided address.</p>
        <button id="popup-ok-btn">Okay</button>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML("beforeend", popupHTML);
  const popup = document.getElementById("package-popup");
  const popupOk = document.getElementById("popup-ok-btn");
  popupOk.addEventListener("click", () => {
    popup.classList.remove("show");
    window.location.href = "pricing.html";
  });

  // ✅ Form submission handler
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
      package: pkg,
      price,
      name: document.getElementById("name").value.trim(),
      email: document.getElementById("email").value.trim(),
      company: document.getElementById("company").value.trim(),
      url: document.getElementById("url").value.trim(),
      businessType: document.getElementById("business-type").value.trim(),
      notes: document.getElementById("notes").value.trim()
    };

    // Basic validation
    if (!data.name || !data.email || !data.company || !data.url || !data.businessType) {
      alert("⚠️ Please fill in all required fields.");
      return;
    }

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      if (res.ok) {
        // ✅ Success: show popup
        popup.classList.add("show");
      } else {
        const err = await res.json().catch(() => ({}));
        alert(err.detail || "Submission failed. Please try again.");
      }
    } catch (err) {
      console.error("Network error:", err);
      alert("Network error. Please check your connection and try again.");
    }
  });
});

