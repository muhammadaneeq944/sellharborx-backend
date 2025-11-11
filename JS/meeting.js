
const calendarEl = document.getElementById("calendar");
const selectedDateDisplay = document.getElementById("selected-date");
const form = document.getElementById("meeting-form");

// Calendar state
const today = new Date();
let currentMonth = today.getMonth();
let currentYear = today.getFullYear();

function renderCalendar(month, year) {
    const monthNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
    const firstDay = new Date(year, month).getDay();
    const daysInMonth = 32 - new Date(year, month, 32).getDate();

    let calendarHTML = `
    <div class="calendar-header">
      <button type="button" class="btn btn-sm btn-light" id="prev">&#8592;</button>
      <span class="month-year">${monthNames[month]} ${year}</span>
      <button type="button" class="btn btn-sm btn-light" id="next">&#8594;</button>
    </div>
    <table class="calendar-table">
      <thead>
        <tr>
          <th>Sun</th><th>Mon</th><th>Tue</th><th>Wed</th>
          <th>Thu</th><th>Fri</th><th>Sat</th>
        </tr>
      </thead>
      <tbody>
  `;

    let date = 1;
    for (let i = 0; i < 6; i++) {
        calendarHTML += "<tr>";
        for (let j = 0; j < 7; j++) {
            if (i === 0 && j < firstDay) {
                calendarHTML += "<td></td>";
            } else if (date > daysInMonth) {
                break;
            } else {
                const fullDate = `${year}-${String(month + 1).padStart(2, "0")}-${String(date).padStart(2, "0")}`;
                calendarHTML += `<td class="calendar-day" data-date="${fullDate}">${date}</td>`;
                date++;
            }
        }
        calendarHTML += "</tr>";
    }

    calendarHTML += "</tbody></table>";
    calendarEl.innerHTML = calendarHTML;

    // Navigation buttons
    document.getElementById("prev").addEventListener("click", () => {
        currentMonth = currentMonth === 0 ? 11 : currentMonth - 1;
        currentYear = currentMonth === 11 ? currentYear - 1 : currentYear;
        renderCalendar(currentMonth, currentYear);
    });

    document.getElementById("next").addEventListener("click", () => {
        currentMonth = currentMonth === 11 ? 0 : currentMonth + 1;
        currentYear = currentMonth === 0 ? currentYear + 1 : currentYear;
        renderCalendar(currentMonth, currentYear);
    });

    // Select date
    document.querySelectorAll(".calendar-day").forEach(day => {
        day.addEventListener("click", () => {
            document.querySelectorAll(".calendar-day").forEach(d => d.classList.remove("selected"));
            day.classList.add("selected");
            selectedDateDisplay.textContent = "Selected Date: " + day.dataset.date;
            selectedDateDisplay.dataset.date = day.dataset.date;
        });
    });
}

renderCalendar(currentMonth, currentYear);


// ✅ REPLACED ONLY THIS PART (backend request instead of alert)
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const agenda = document.getElementById("agenda").value;
    const date = selectedDateDisplay.dataset.date;

    if (!date) {
        alert("Please select a date for the meeting.");
        return;
    }

    try {
         const res = await fetch("http://127.0.0.1:8000/book-meeting", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name,
                email,
                agenda,
                date,
                phone: "",
                time: ""
            })
        });

        if (res.ok) {
            showMeetingPopup();
            return;
        }

        if (res.status === 409) {
            const e = await res.json();
            alert(e.detail || "You already booked for this date.");
            return;
        }

        const e = await res.json();
        alert(e.detail || "Booking failed.");

    } catch (err) {
        console.error(err);
        alert("Network error. Try later.");
    }
});

// SUCCESS POPUP FOR MEETING
function showMeetingPopup() {
  const popup = document.createElement("div");
  popup.id = "meeting-popup";
  popup.innerHTML = `
    <div class="mp-modal">
        <h2>✅ Meeting Booked Successfully!</h2>
        <p>Thank you for booking a meeting with <b>Sell Harbor X</b>.</p>
        <p>Our team will reach out shortly to finalize the time and next steps.</p>
        <ul style="margin-top:10px;text-align:left;max-width:600px;">
          <li>Personalized guidance on your case</li>
          <li>Free initial consultation</li>
          <li>Strategic roadmap & recommendations</li>
        </ul>
        <p style="margin-top:15px;">Redirecting you to Home...</p>
    </div>
  `;
  document.body.appendChild(popup);

  setTimeout(() => {
    window.location.href = "/index.html";
  }, 4000);
}



// --- Append this to backend/JS/meeting.js (bottom) ---
// document.addEventListener("DOMContentLoaded", () => {
//   const form = document.getElementById("meeting-form");
//   const selectedDateDisplay = document.getElementById("selected-date");

//   if (!form) return; // safe-guard if this file loads on pages without the form

//   form.addEventListener("submit", async (e) => {
//     e.preventDefault();

//     const name = (document.getElementById("name") || {}).value?.trim() || "";
//     const email = (document.getElementById("email") || {}).value?.trim() || "";
//     const agenda = (document.getElementById("agenda") || {}).value?.trim() || "";
//     const date = selectedDateDisplay?.dataset?.date;

//     if (!date) {
//       alert("Please select a date for the meeting.");
//       return;
//     }
//     if (!name || !email || !agenda) {
//       alert("Please fill all required fields.");
//       return;
//     }

//     try {
//       const res = await fetch("http://127.0.0.1:8000/book-meeting", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ name, email, agenda, date })
//       });

//       if (res.ok) {
//         // success: set flash & redirect to index.html
//         localStorage.setItem("meeting_flash", "Meeting booked! Explore more services.");
//         window.location.href = "/index.html";
//         return;
//       }

//       if (res.status === 409) {
//         const err = await res.json().catch(()=>({}));
//         alert(err.detail || "You already booked a meeting for this date.");
//         return;
//       }

//       const err = await res.json().catch(()=>({}));
//       alert(err.detail || "Failed to book meeting. Try again later.");
//     } catch (err) {
//       console.error("Booking error:", err);
//       alert("Network error. Please try again.");
//     }
//   });
// });
