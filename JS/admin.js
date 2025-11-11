// backend/JS/admin.js
let currentContactId = null;

const API_BASE = "http://127.0.0.1:8000";
const auditsList = document.getElementById("auditsList");
const loginForm = document.getElementById("adminLoginForm");
const loginMessage = document.getElementById("loginMessage");
const loginSection = document.getElementById("loginSection");
const dashboardSection = document.getElementById("dashboardSection");
const usersList = document.getElementById("usersList");
const meetingsList = document.getElementById("meetingsList");
const logoutBtn = document.getElementById("logoutBtn");
const contactsList = document.getElementById("contactsList");
const newslettersList = document.getElementById("newslettersList");



function saveToken(token) { localStorage.setItem("admin_token", token); }
function getToken() { return localStorage.getItem("admin_token"); }
function clearToken() { localStorage.removeItem("admin_token"); }

async function apiFetch(path, opts = {}) {
    const token = getToken();
    opts.headers = opts.headers || {};
    if (!opts.headers["Content-Type"] && !(opts.body instanceof FormData)) {
        opts.headers["Content-Type"] = "application/json";
    }
    if (token) opts.headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(API_BASE + path, opts);
    if (res.status === 401) { // token expired or invalid
        clearToken();
        showLogin("Session expired. Please login again.");
        throw new Error("Unauthorized");
    }
    return res;
}

function showLogin(msg) {
    loginSection.style.display = "block";
    dashboardSection.style.display = "none";
    if (msg) { loginMessage.textContent = msg; loginMessage.style.display = "block"; }
    else { loginMessage.style.display = "none"; }
}
function showDashboard() {
    loginSection.style.display = "none";
    dashboardSection.style.display = "block";
    loginMessage.style.display = "none";
}

// Init: check token and show dashboard if valid
(async function init() {
    const token = getToken();
    if (!token) { showLogin(); return; }
    try {
        const res = await apiFetch("/admin/me", { method: "GET" });
        if (!res.ok) { showLogin(); return; }
        showDashboard();
        loadUsers();
        loadMeetings();
        loadAudits();
        loadContacts();
        loadNewsletters();
        loadPackages();



    } catch (err) {
        console.error("Init error:", err);
        showLogin();
    }
})();

// Login
loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const username = document.getElementById("adminUsername").value.trim();
    const password = document.getElementById("adminPassword").value;
    if (!username || !password) { showLogin("Please fill username and password."); return; }

    try {
        const res = await fetch(API_BASE + "/admin/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => null);
            showLogin(err?.detail || "Login failed.");
            return;
        }

        const data = await res.json();
        saveToken(data.access_token);
        showDashboard();
        loadUsers();
    } catch (err) {
        console.error("Login error:", err);
        showLogin("Could not reach server.");
    }
});

// Logout
logoutBtn.addEventListener("click", function () { clearToken(); showLogin(); });

// Render helpers
function emptyChildren(el) { while (el.firstChild) el.removeChild(el.firstChild); }

// Load and render users as advanced table with Edit/Delete
async function loadUsers() {
    usersList.innerHTML = "<p>Loading users...</p>";
    try {
        const res = await apiFetch("/admin/users", { method: "GET" });
        if (!res.ok) {
            usersList.innerHTML = "<p>Failed to load users.</p>";
            return;
        }
        const users = await res.json();
        renderUsersTable(users);
    } catch (err) {
        usersList.innerHTML = "<p>Error loading users.</p>";
        console.error(err);
    }
}

function renderUsersTable(users) {
    emptyChildren(usersList);
    const table = document.createElement("table");
    table.className = "admin-users-table";
    table.style.width = "100%";
    table.style.borderCollapse = "collapse";

    // Header
    const thead = document.createElement("thead");
    thead.innerHTML = `<tr>
        <th style="text-align:left;padding:8px;border-bottom:1px solid #ddd">Username</th>
        <th style="text-align:left;padding:8px;border-bottom:1px solid #ddd">Email</th>
        <th style="text-align:left;padding:8px;border-bottom:1px solid #ddd">Actions</th>
    </tr>`;
    table.appendChild(thead);

    // Body
    const tbody = document.createElement("tbody");
    users.forEach(u => {
        const tr = document.createElement("tr");
        tr.dataset.id = u.id || u._id || "";
        tr.innerHTML = `
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(u.username || "")}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(u.email || "")}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">
                <button class="btn small edit-btn">Edit</button>
                <button class="btn small danger delete-btn">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    usersList.appendChild(table);

    // Attach handlers
    table.querySelectorAll(".delete-btn").forEach(btn => {
        btn.addEventListener("click", (ev) => {
            const tr = ev.target.closest("tr");
            const userId = tr.dataset.id;
            confirmAndDeleteUser(userId);
        });
    });

    table.querySelectorAll(".edit-btn").forEach(btn => {
        btn.addEventListener("click", (ev) => {
            const tr = ev.target.closest("tr");
            const userId = tr.dataset.id;
            const username = tr.children[0].textContent;
            const email = tr.children[1].textContent;
            openEditModal(userId, username, email);
        });
    });
}

// Utility: simple escape
function escapeHtml(s) {
    return s.replace(/[&<>"']/g, function (m) { return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]); });
}

// Confirm & delete
async function confirmAndDeleteUser(userId) {
    if (!confirm("Are you sure you want to permanently delete this user?")) return;
    try {
        const res = await apiFetch(`/admin/users/${userId}`, { method: "DELETE" });
        if (res.status === 204) {
            alert("User deleted.");
            loadUsers();
            return;
        }
        const err = await res.json().catch(() => null);
        alert(err?.detail || "Failed to delete user.");
    } catch (err) {
        alert("Error deleting user.");
        console.error(err);
    }
}

// Edit modal (simple prompt-based UI — you can replace with nicer modal)
async function openEditModal(userId, currentUsername = "", currentEmail = "") {
    // Use prompt for quickness: first ask username, then email, then ask if change password
    const newUsername = prompt("Edit username:", currentUsername);
    if (newUsername === null) return; // cancelled
    const newEmail = prompt("Edit email:", currentEmail);
    if (newEmail === null) return;

    const changePassword = confirm("Do you want to change the user's password?");
    let newPassword = null;
    if (changePassword) {
        newPassword = prompt("Enter new password (will be hashed):");
        if (newPassword === null) return;
        if (newPassword.length === 0) { alert("Password cannot be empty."); return; }
        // Enforce bcrypt 72-byte limit (server will also check)
        if (new TextEncoder().encode(newPassword).length > 72) {
            alert("Password too long (max 72 bytes). Choose a shorter password.");
            return;
        }
    }

    // Build payload with only changed fields
    const payload = {};
    if (newUsername !== currentUsername) payload.username = newUsername;
    if (newEmail !== currentEmail) payload.email = newEmail;
    if (newPassword) payload.password = newPassword;

    if (Object.keys(payload).length === 0) { alert("No changes made."); return; }

    try {
        const res = await apiFetch(`/admin/users/${userId}`, {
            method: "PUT",
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const err = await res.json().catch(() => null);
            alert(err?.detail || "Failed to update user.");
            return;
        }
        const updated = await res.json();
        alert("User updated.");
        loadUsers();
    } catch (err) {
        alert("Error updating user.");
        console.error(err);
    }
}









// Metting.py

// -------------------------
// Meetings: load & render
// -------------------------
async function loadMeetings() {
    if (!meetingsList) return;
    meetingsList.innerHTML = "<p>Loading meetings...</p>";
    try {
        const res = await apiFetch("/admin/meetings", { method: "GET" });
        if (!res.ok) {
            meetingsList.innerHTML = "<p>Failed to load meetings.</p>";
            return;
        }
        const meetings = await res.json();
        renderMeetingsTable(meetings);
    } catch (err) {
        meetingsList.innerHTML = "<p>Error loading meetings.</p>";
        console.error(err);
    }
}

function renderMeetingsTable(meetings) {
    if (!meetingsList) return;
    emptyChildren(meetingsList);

    const table = document.createElement("table");
    table.className = "admin-meetings-table";
    table.style.width = "100%";
    table.style.borderCollapse = "collapse";

    const thead = document.createElement("thead");
    thead.innerHTML = `<tr>
        <th style="text-align:left;padding:8px;border-bottom:1px solid #ddd">Name</th>
        <th style="text-align:left;padding:8px;border-bottom:1px solid #ddd">Email</th>
        <th style="text-align:left;padding:8px;border-bottom:1px solid #ddd">Agenda</th>
        <th style="text-align:left;padding:8px;border-bottom:1px solid #ddd">Date</th>
        <th style="text-align:left;padding:8px;border-bottom:1px solid #ddd">Created At (UTC)</th>
        <th style="text-align:left;padding:8px;border-bottom:1px solid #ddd">Actions</th>
    </tr>`;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    meetings.forEach(m => {
        const tr = document.createElement("tr");
        tr.dataset.id = m.id || "";
        tr.innerHTML = `
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(m.name || "")}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(m.email || "")}</td>
            <td style="padding:8px;border-bottom:1px solid #eee; max-width:400px; white-space:pre-wrap;">${escapeHtml(m.agenda || "")}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(m.date || "")}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(m.created_at ? m.created_at.replace("T", " ").split(".")[0] : "")}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">
                <button class="btn small danger delete-meeting-btn">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    meetingsList.appendChild(table);

    // Attach delete handlers (with confirmation)
    table.querySelectorAll(".delete-meeting-btn").forEach(btn => {
        btn.addEventListener("click", async (ev) => {
            const tr = ev.target.closest("tr");
            const meetingId = tr.dataset.id;
            if (!confirm("Are you sure you want to permanently delete this meeting?")) return;
            try {
                const res = await apiFetch(`/admin/meetings/${meetingId}`, { method: "DELETE" });
                if (res.status === 204) {
                    alert("Meeting deleted.");
                    loadMeetings();
                    return;
                }
                const err = await res.json().catch(()=>null);
                alert(err?.detail || "Failed to delete meeting.");
            } catch (err) {
                console.error("Delete meeting error:", err);
                alert("Error deleting meeting.");
            }
        });
    });
}
// -------------------------
// Render audits table
// -------------------------
// -------------------------
// Audits: load & render
// -------------------------
async function loadAudits() {
    if (!auditsList) return;
    auditsList.innerHTML = "<p>Loading audits...</p>";
    try {
        const res = await apiFetch("/admin/audits", { method: "GET" });
        if (!res.ok) {
            auditsList.innerHTML = "<p>Failed to load audits.</p>";
            return;
        }
        const audits = await res.json();
        renderAuditsTable(audits);
    } catch (err) {
        auditsList.innerHTML = "<p>Error loading audits.</p>";
        console.error(err);
    }
}



function renderAuditsTable(audits) {
    emptyChildren(auditsList);

    if (!audits.length) {
        auditsList.innerHTML = "<p>No audit requests yet.</p>";
        return;
    }

    const table = document.createElement("table");
    table.className = "admin-audits-table";
    table.style.width = "100%";
    table.style.borderCollapse = "collapse";

    const thead = document.createElement("thead");
    thead.innerHTML = `
        <tr>
            <th style="padding:8px;border-bottom:1px solid #ddd">Name</th>
            <th style="padding:8px;border-bottom:1px solid #ddd">Email</th>
            <th style="padding:8px;border-bottom:1px solid #ddd">Brand</th>
            <th style="padding:8px;border-bottom:1px solid #ddd">Product URL</th>
            <th style="padding:8px;border-bottom:1px solid #ddd">Message</th>
            <th style="padding:8px;border-bottom:1px solid #ddd">Created At (UTC)</th>
            <th style="padding:8px;border-bottom:1px solid #ddd">Actions</th>
        </tr>`;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    audits.forEach(a => {
        const tr = document.createElement("tr");
        tr.dataset.id = a.id;
        tr.innerHTML = `
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(a.firstname + " " + a.lastname)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(a.email)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(a.brandname)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(a.producturl)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee; max-width:300px; white-space:pre-wrap;">${escapeHtml(a.message)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(a.created_at ? a.created_at.replace("T"," ").split(".")[0] : "")}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">
                <button class="btn small danger delete-audit-btn">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    auditsList.appendChild(table);

    // bind delete handlers
    table.querySelectorAll(".delete-audit-btn").forEach(btn => {
        btn.addEventListener("click", async (ev) => {
            const tr = ev.target.closest("tr");
            const auditId = tr.dataset.id;
            if (!confirm("Delete this audit request?")) return;
            const res = await apiFetch(`/admin/audits/${auditId}`, { method: "DELETE" });
            if (res.status === 204) {
                loadAudits();
            } else {
                alert("Failed to delete");
            }
        });
    });
}



// -------------------------
// Contacts: load & render
// -------------------------
async function loadContacts() {
    if (!contactsList) return;
    contactsList.innerHTML = "<p>Loading contacts...</p>";
    try {
        const res = await apiFetch("/admin/contacts", { method: "GET" });
        if (!res.ok) {
            contactsList.innerHTML = "<p>Failed to load contacts.</p>";
            return;
        }
        const contacts = await res.json();
        renderContactsTable(contacts);
    } catch (err) {
        console.error(err);
        contactsList.innerHTML = "<p>Error loading contacts.</p>";
    }
}

function renderContactsTable(contacts) {
    emptyChildren(contactsList);
    if (!contacts.length) {
        contactsList.innerHTML = "<p>No contact requests.</p>";
        return;
    }

    const table = document.createElement("table");
    table.style.width = "100%";
    table.style.borderCollapse = "collapse";

    table.innerHTML = `
        <thead>
            <tr>
                <th style="padding:8px;border-bottom:1px solid #ddd">Name</th>
                <th style="padding:8px;border-bottom:1px solid #ddd">Email</th>
                <th style="padding:8px;border-bottom:1px solid #ddd">Subject</th>
                <th style="padding:8px;border-bottom:1px solid #ddd">Created At</th>
                <th style="padding:8px;border-bottom:1px solid #ddd">Actions</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;

    const tbody = table.querySelector("tbody");

    contacts.forEach(c => {
        const tr = document.createElement("tr");
        tr.dataset.id = c.id;
        tr.innerHTML = `
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(c.firstname)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(c.email)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(c.subject)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(c.created_at?.replace("T"," ").split(".")[0] || "")}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">
                <button class="btn small view-contact-btn">View</button>
                <button class="btn small danger delete-contact-btn">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    contactsList.appendChild(table);

    // delete handler
    table.querySelectorAll(".delete-contact-btn").forEach(btn => {
        btn.addEventListener("click", async (ev) => {
            if (!confirm("Delete this contact request?")) return;
            const id = btn.closest("tr").dataset.id;
            const res = await apiFetch(`/admin/contacts/${id}`, { method: "DELETE" });
            if (res.status === 204) loadContacts();
            else alert("Failed to delete contact");
        });
    });
    // VIEW handler (inside renderContactsTable)
table.querySelectorAll(".view-contact-btn").forEach(btn => {
    btn.addEventListener("click", (ev) => {
        const tr = btn.closest("tr");
        const id = tr.dataset.id;
        currentContactId = id;

        // find this contact object
        const c = contacts.find(x => x.id === id);
        openContactModal(c);
    });
});


    // later view modal will be added here
}





const contactModal = document.getElementById("contactModal");
const closeContactModal = document.getElementById("closeContactModal");
const deleteContactInside = document.getElementById("deleteContactInside");

function openContactModal(c) {
    document.getElementById("mName").textContent = c.firstname;
    document.getElementById("mEmail").textContent = c.email;
    document.getElementById("mSubject").textContent = c.subject;
    document.getElementById("mMessage").textContent = c.message || "";
    document.getElementById("mCreated").textContent = c.created_at?.replace("T"," ").split(".")[0] || "";
    contactModal.style.display = "flex";
}

closeContactModal.onclick = () => { contactModal.style.display = "none"; }

deleteContactInside.onclick = async () => {
    if (!confirm("Delete this contact?")) return;
    const res = await apiFetch(`/admin/contacts/${currentContactId}`, { method:"DELETE" });
    if (res.status === 204) {
        contactModal.style.display = "none";
        loadContacts();
    } else {
        alert("Delete failed");
    }
};



async function loadNewsletters() {
    if (!newslettersList) return;
    newslettersList.innerHTML = "<p>Loading...</p>";
    try {
        const res = await apiFetch("/admin/newsletters", { method: "GET" });
        const data = await res.json();
        renderNewsletterTable(data);
    } catch (err) {
        newslettersList.innerHTML = "<p>Error loading.</p>";
    }
}

function renderNewsletterTable(rows) {
    emptyChildren(newslettersList);
    if (!rows.length) {
        newslettersList.innerHTML = "<p>No subscribers yet.</p>";
        return;
    }

    const table = document.createElement("table");
    table.style.width = "100%";
    table.innerHTML = `
      <thead>
        <tr>
          <th>Email</th>
          <th>Subscribed At</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody></tbody>
    `;
    const tbody = table.querySelector("tbody");

    rows.forEach(r => {
        const tr = document.createElement("tr");
        tr.dataset.id = r.id;
        tr.innerHTML = `
          <td>${escapeHtml(r.email)}</td>
          <td>${escapeHtml(r.created_at?.replace("T"," ").split(".")[0] || "")}</td>
          <td>
            <button class="btn small danger delete-newsletter-btn">Delete</button>
          </td>
        `;
        tbody.appendChild(tr);
    });

    newslettersList.appendChild(table);

    table.querySelectorAll(".delete-newsletter-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            if (!confirm("Delete this subscriber?")) return;
            const id = btn.closest("tr").dataset.id;
            const res = await apiFetch(`/admin/newsletters/${id}`, { method:"DELETE" });
            if (res.status === 204) loadNewsletters();
            else alert("Failed to delete");
        });
    });
}




// -------------------------
// Package Requests: load & render
// -------------------------
async function loadPackages() {
    const packagesList = document.getElementById("packagesList");
    if (!packagesList) return;
    packagesList.innerHTML = "<p>Loading package requests...</p>";

    try {
        const res = await apiFetch("/admin/packages", { method: "GET" });
        if (!res.ok) {
            packagesList.innerHTML = "<p>Failed to load packages.</p>";
            return;
        }
        const data = await res.json();
        renderPackagesTable(data);
    } catch (err) {
        console.error("Error loading packages:", err);
        packagesList.innerHTML = "<p>Error loading packages.</p>";
    }
}

function renderPackagesTable(rows) {
    const packagesList = document.getElementById("packagesList");
    emptyChildren(packagesList);

    if (!rows.length) {
        packagesList.innerHTML = "<p>No package requests yet.</p>";
        return;
    }

    const table = document.createElement("table");
    table.style.width = "100%";
    table.style.borderCollapse = "collapse";

    table.innerHTML = `
        <thead>
            <tr>
                <th style="padding:8px;border-bottom:1px solid #ddd">Name</th>
                <th style="padding:8px;border-bottom:1px solid #ddd">Email</th>
                <th style="padding:8px;border-bottom:1px solid #ddd">Package</th>
                <th style="padding:8px;border-bottom:1px solid #ddd">Price</th>
                <th style="padding:8px;border-bottom:1px solid #ddd">Business name</th>
                <th style="padding:8px;border-bottom:1px solid #ddd">Business Url</th>
                <th style="padding:8px;border-bottom:1px solid #ddd">Created At</th>
                <th style="padding:8px;border-bottom:1px solid #ddd">Actions</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;

    const tbody = table.querySelector("tbody");

    rows.forEach(r => {
        const tr = document.createElement("tr");
        tr.dataset.id = r.id;
        tr.innerHTML = `
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(r.name)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(r.email)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(r.package)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(r.price)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(r.company)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(r.url)}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">${escapeHtml(r.created_at?.replace("T"," ").split(".")[0] || "")}</td>
            <td style="padding:8px;border-bottom:1px solid #eee">
                <button class="btn small danger delete-package-btn">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    packagesList.appendChild(table);

    // Delete handler
    table.querySelectorAll(".delete-package-btn").forEach(btn => {
        btn.addEventListener("click", async () => {
            const id = btn.closest("tr").dataset.id;
            if (!confirm("Delete this package request?")) return;
            const res = await apiFetch(`/admin/packages/${id}`, { method: "DELETE" });
            if (res.status === 204) loadPackages();
            else alert("Failed to delete package.");
        });
    });
}


