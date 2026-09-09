// VibeVoyage - App Logic with Full Stack API integrations
// ==========================================================================
// 1. STATE & VARIABLES
// ==========================================================================
let currentUser = null;
let trips = [];
let currentTripId = null;
let activeDayIndex = 0;
let map = null;
let mapMarkers = [];
let mapPolyline = null;
let isAuthModeLogin = true;
// Default dummy data (used as local fallback if server connection fails)
const FALLBACK_TRIPS = [
  {
    id: "trip-tokyo-fallback",
    destination: "Tokyo, Japan (Offline)",
    startDate: "2026-06-01",
    endDate: "2026-06-07",
    budget: 3000,
    vibe: "adventure",
    lat: 35.6762,
    lng: 139.6503,
    activities: [
      {
        id: "act-1",
        day: 0,
        name: "Shibuya Stream Hotel Check-in",
        time: "14:00",
        cost: 250,
        location: "Shibuya Stream, Tokyo",
        category: "hotel",
        notes: "Fallback data mode",
        lat: 35.6580,
        lng: 139.7016
      }
    ],
    checklist: [
      { id: "chk-1", text: "Create your server-backed trip blueprints", checked: false }
    ]
  }
];
const VIBE_IMAGES = {
  relaxation: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80",
  adventure: "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=600&q=80",
  cultural: "https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&w=600&q=80",
  foodie: "https://images.unsplash.com/photo-1498654896293-37aacf113fd9?auto=format&fit=crop&w=600&q=80"
};
const DESTINATION_GALLERY = {
  tokyo: [
    "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1540959733332-eab4deceeaf7?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1524413840807-0c3cb6fa808d?auto=format&fit=crop&w=300&q=80"
  ],
  paris: [
    "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1499856871958-5b9647a6409a?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1509060464153-44667396260f?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1522083165195-342750297f46?auto=format&fit=crop&w=300&q=80"
  ],
  default: [
    "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1506012787146-f92b2d7d6d96?auto=format&fit=crop&w=300&q=80",
    "https://images.unsplash.com/photo-1433832597046-4f10e10ac764?auto=format&fit=crop&w=300&q=80"
  ]
};
// ==========================================================================
// 2. APP INITIALIZATION
// ==========================================================================
window.addEventListener("DOMContentLoaded", () => {
  // Create dynamic import triggers
  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.id = "trip-import-file";
  fileInput.accept = ".json";
  fileInput.style.display = "none";
  fileInput.addEventListener("change", handleImportFile);
  document.body.appendChild(fileInput);
  checkAuthSession();
});
// Check for active login session
async function checkAuthSession() {
  const loggedUser = localStorage.getItem("vibevoyage_user");
  if (loggedUser) {
    currentUser = loggedUser;
    setNavUserNames();
    const success = await loadTripsFromServer();
    if (success) {
      showDashboard();
      showToast(`Logged in backend: ${currentUser}`, "success");
    } else {
      // Server down or unauthorized
      showToast("Server unavailable. Operating in local mode.", "warning");
      loadFallbackData();
      showDashboard();
    }
  } else {
    showView("auth-section");
  }
}
function showView(sectionId) {
  document.querySelectorAll(".view-section").forEach(sec => {
    sec.classList.remove("active");
  });
  const activeSec = document.getElementById(sectionId);
  if (activeSec) {
    activeSec.classList.add("active");
  }
  if (sectionId === "planner-section") {
    setTimeout(initMapIfNeeded, 300);
  }
}
function setNavUserNames() {
  document.getElementById("user-display-name").innerText = currentUser;
  document.getElementById("user-display-name-planner").innerText = currentUser;
}
// Loads local fallback array in case backend goes offline
function loadFallbackData() {
  trips = JSON.parse(JSON.stringify(FALLBACK_TRIPS));
}
// ==========================================================================
// 3. API CLIENT ACTIONS
// ==========================================================================
// GET Trips
async function loadTripsFromServer() {
  try {
    const response = await fetch('/api/trips', {
      headers: {
        'Authorization': currentUser
      }
    });
    
    if (response.ok) {
      trips = await response.json();
      return true;
    }
    return false;
  } catch (err) {
    console.error("API load trips failed", err);
    return false;
  }
}
// POST Trip
async function createTripOnServer(tripObj) {
  try {
    const response = await fetch('/api/trips', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': currentUser
      },
      body: JSON.stringify(tripObj)
    });
    
    if (response.ok) {
      const savedTrip = await response.json();
      // Replace mock object with database validated object
      const idx = trips.findIndex(t => t.id === tripObj.id);
      if (idx !== -1) {
        trips[idx] = savedTrip;
      } else {
        trips.push(savedTrip);
      }
      renderTripsList();
      showToast("Trip synced to server", "success");
      
      // Load the newly created workspace
      loadTripWorkspace(savedTrip.id);
      return true;
    }
    return false;
  } catch (err) {
    showToast("Failed to sync trip to server database", "error");
    return false;
  }
}
// PUT Trip updates
async function updateTripOnServer(tripId) {
  const trip = trips.find(t => t.id === tripId);
  if (!trip) return;
  
  try {
    const response = await fetch(`/api/trips/${tripId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': currentUser
      },
      body: JSON.stringify(trip)
    });
    
    if (response.ok) {
      const updated = await response.json();
      const idx = trips.findIndex(t => t.id === tripId);
      if (idx !== -1) {
        trips[idx] = updated;
      }
      return true;
    }
    return false;
  } catch (err) {
    console.warn("Failed to sync updates to backend", err);
    return false;
  }
}
// DELETE Trip
async function deleteTripFromServer(tripId) {
  try {
    const response = await fetch(`/api/trips/${tripId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': currentUser
      }
    });
    return response.ok;
  } catch (err) {
    console.error("API delete failed", err);
    return false;
  }
}
// ==========================================================================
// 4. AUTHENTICATION CONTROLLERS
// ==========================================================================
function toggleAuthMode() {
  isAuthModeLogin = !isAuthModeLogin;
  const title = document.getElementById("auth-card-title");
  const button = document.getElementById("btn-auth-submit");
  const msg = document.getElementById("auth-toggle-msg");
  
  if (isAuthModeLogin) {
    title.innerText = "Sign In";
    button.innerText = "Sign In";
    msg.innerHTML = `New to VibeVoyage? <span onclick="toggleAuthMode()">Create an account</span>`;
  } else {
    title.innerText = "Create Account";
    button.innerText = "Sign Up";
    msg.innerHTML = `Already have an account? <span onclick="toggleAuthMode()">Sign In</span>`;
  }
}
async function handleAuthSubmit(e) {
  e.preventDefault();
  const username = document.getElementById("auth-username").value.trim();
  const password = document.getElementById("auth-password").value;
  
  if (!username || !password) {
    showToast("Please fill all fields", "error");
    return;
  }
  
  const url = isAuthModeLogin ? '/api/auth/login' : '/api/auth/register';
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    });
    
    const result = await response.json();
    
    if (response.ok) {
      currentUser = result.username;
      localStorage.setItem("vibevoyage_user", currentUser);
      setNavUserNames();
      
      showToast(isAuthModeLogin ? "Login successful" : "Account created & loaded!", "success");
      document.getElementById("auth-form").reset();
      
      await loadTripsFromServer();
      showDashboard();
    } else {
      showToast(result.error || "Authentication failed", "error");
    }
  } catch (err) {
    // Failover local bypass for demo when no backend is running
    showToast("Server offline. Booting in localStorage Local Mode", "warning");
    currentUser = username;
    localStorage.setItem("vibevoyage_user", currentUser);
    setNavUserNames();
    loadFallbackData();
    showDashboard();
  }
}
function handleLogout() {
  currentUser = null;
  trips = [];
  currentTripId = null;
  localStorage.removeItem("vibevoyage_user");
  showToast("Logged out successfully", "warning");
  showView("auth-section");
  if (map) {
    map.remove();
    map = null;
  }
}
// ==========================================================================
// 5. TRIPS DASHBOARD RENDERER
// ==========================================================================
function showDashboard() {
  showView("dashboard-section");
  renderTripsList();
}
function renderTripsList() {
  const container = document.getElementById("trips-grid");
  container.innerHTML = "";
  
  if (trips.length === 0) {
    container.innerHTML = `
      <div class="glass-panel" style="grid-column: 1/-1; padding: 50px; text-align: center;">
        <p style="font-size: 1.1rem; color: var(--text-muted); margin-bottom: 20px;">No trips mapped yet. Let's create your first itinerary!</p>
        <button class="btn btn-primary" onclick="openTripModal()">Design New Trip</button>
      </div>
    `;
    return;
  }
  
  trips.forEach(trip => {
    const totalCost = trip.activities.reduce((sum, act) => sum + Number(act.cost), 0);
    const budgetPercent = Math.min(Math.round((totalCost / trip.budget) * 100), 100);
    const isOverBudget = totalCost > trip.budget;
    const bgImage = VIBE_IMAGES[trip.vibe] || VIBE_IMAGES.relaxation;
    const dayCount = getDaysCount(trip.startDate, trip.endDate);
    const formattedDates = `${formatDate(trip.startDate)} - ${formatDate(trip.endDate)}`;
    
    const card = document.createElement("div");
    card.className = "glass-panel trip-card";
    card.innerHTML = `
      <div class="trip-img-wrap" style="background-image: url('${bgImage}')">
        <div class="trip-img-overlay"></div>
        <span class="trip-badge vibe-${trip.vibe}">${trip.vibe}</span>
      </div>
      <div class="trip-card-body">
        <h3 class="trip-card-title">${escapeHtml(trip.destination)}</h3>
        <div class="trip-card-dates">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
          ${formattedDates}
        </div>
        
        <div style="margin-bottom: 20px;">
          <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 5px;">
            <span style="color: var(--text-muted);">Expenses vs Budget</span>
            <span style="font-weight: 600; color: ${isOverBudget ? 'var(--accent-rose)' : 'var(--accent-emerald)'}">
              $${totalCost} / $${trip.budget} (${budgetPercent}%)
            </span>
          </div>
          <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.05); border-radius: 3px; overflow: hidden;">
            <div style="width: ${budgetPercent}%; height: 100%; background: ${isOverBudget ? 'var(--accent-rose)' : 'var(--primary-gradient)'}; border-radius: 3px;"></div>
          </div>
        </div>
        <div class="trip-card-meta">
          <div class="meta-item">
            <span class="meta-label">Duration</span>
            <span class="meta-val">${dayCount} Days</span>
          </div>
          <div style="display: flex; gap: 8px;">
            <button class="btn btn-secondary" onclick="event.stopPropagation(); loadTripWorkspace('${trip.id}')" style="padding: 6px 12px; font-size: 0.8rem;">Explore</button>
            <button class="btn btn-danger btn-icon" onclick="event.stopPropagation(); deleteTrip('${trip.id}')" style="width: 32px; height: 32px;" title="Delete Trip">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
            </button>
          </div>
        </div>
      </div>
    `;
    
    card.addEventListener("click", () => loadTripWorkspace(trip.id));
    container.appendChild(card);
  });
}
// ==========================================================================
// 6. TRIP BLUEPRINT MODALS
// ==========================================================================
function openTripModal() {
  document.getElementById("trip-modal").classList.add("active");
  const today = new Date().toISOString().split("T")[0];
  const nextWeek = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split("T")[0];
  document.getElementById("trip-start").value = today;
  document.getElementById("trip-end").value = nextWeek;
  document.querySelectorAll(".vibe-option").forEach(opt => opt.classList.remove("selected"));
  document.querySelector(".vibe-option[data-vibe='relaxation']").classList.add("selected");
}
function closeTripModal() {
  document.getElementById("trip-modal").classList.remove("active");
  document.getElementById("trip-form").reset();
}
function selectVibeOption(element) {
  document.querySelectorAll(".vibe-option").forEach(opt => opt.classList.remove("selected"));
  element.classList.add("selected");
}
async function handleTripSubmit(e) {
  e.preventDefault();
  const dest = document.getElementById("trip-destination").value.trim();
  const start = document.getElementById("trip-start").value;
  const end = document.getElementById("trip-end").value;
  const budget = Number(document.getElementById("trip-budget").value);
  const vibe = document.querySelector(".vibe-option.selected").getAttribute("data-vibe");
  
  if (new Date(start) > new Date(end)) {
    showToast("Start date must be before End date", "error");
    return;
  }
  
  const mockId = "trip-" + Date.now();
  const fallbackCoords = getMockCoords(dest);
  
  const newTrip = {
    id: mockId,
    destination: dest,
    startDate: start,
    endDate: end,
    budget: budget,
    vibe: vibe,
    lat: fallbackCoords[0],
    lng: fallbackCoords[1],
    activities: [],
    checklist: [
      { id: `chk-${Date.now()}-1`, text: "Book flight/train tickets", checked: false },
      { id: `chk-${Date.now()}-2`, text: "Check hotel reservations", checked: false },
      { id: `chk-${Date.now()}-3`, text: "Pack appropriate clothes", checked: false }
    ]
  };
  
  // Try geocoding online before pushing to server
  try {
    const geoQuery = encodeURIComponent(dest);
    const geoRes = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${geoQuery}&limit=1`);
    const geoData = await geoRes.json();
    if (geoData && geoData.length > 0) {
      newTrip.lat = parseFloat(geoData[0].lat);
      newTrip.lng = parseFloat(geoData[0].lon);
    }
  } catch (err) {
    console.warn("Geocoding failed; using fallback hash coords.");
  }
  
  // Push to server or fallback local array
  const success = await createTripOnServer(newTrip);
  
  if (!success) {
    // Offline local fallback
    trips.push(newTrip);
    closeTripModal();
    loadTripWorkspace(newTrip.id);
    showToast(`Created trip offline to ${dest}`, "warning");
  } else {
    closeTripModal();
  }
}
async function deleteTrip(tripId) {
  if (confirm("Are you sure you want to delete this trip blueprint? This cannot be undone.")) {
    const success = await deleteTripFromServer(tripId);
    
    trips = trips.filter(t => t.id !== tripId);
    saveTripsData();
    renderTripsList();
    
    if (success) {
      showToast("Trip blueprint deleted from server", "success");
    } else {
      showToast("Trip deleted locally", "warning");
    }
  }
}
// Helper to save data to localStorage when operating offline
function saveTripsData() {
  if (!currentUser) return;
  // If we are in local offline failover mode, we write to localStorage
  const userTripsKey = `vibevoyage_trips_${currentUser}`;
  localStorage.setItem(userTripsKey, JSON.stringify(trips));
}
// ==========================================================================
// 7. ITINERARY WORKSPACE LOGIC
// ==========================================================================
function loadTripWorkspace(tripId) {
  currentTripId = tripId;
  activeDayIndex = 0;
  
  const trip = trips.find(t => t.id === tripId);
  if (!trip) {
    showToast("Trip not found", "error");
    showDashboard();
    return;
  }
  
  document.getElementById("planner-trip-title").innerText = trip.destination;
  
  const daysCount = getDaysCount(trip.startDate, trip.endDate);
  const formattedDates = `${formatDate(trip.startDate)} - ${formatDate(trip.endDate)}`;
  document.getElementById("planner-trip-subtitle").innerHTML = `
    <span class="trip-badge vibe-${trip.vibe}" style="position: static; vertical-align: middle; margin-right: 8px;">${trip.vibe}</span>
    ${formattedDates} &bull; ${daysCount} Days
  `;
  
  showView("planner-section");
  
  renderDayTabs(daysCount);
  renderDayTimeline();
  renderBudgetStats();
  renderChecklist();
  renderLocalGallery(trip.destination);
  
  updateMapLocation();
}
function renderDayTabs(daysCount) {
  const tabsContainer = document.getElementById("day-tabs");
  tabsContainer.innerHTML = "";
  
  for (let i = 0; i < daysCount; i++) {
    const tab = document.createElement("div");
    tab.className = `day-tab ${i === activeDayIndex ? 'active' : ''}`;
    tab.innerText = `Day ${i + 1}`;
    tab.addEventListener("click", () => {
      activeDayIndex = i;
      document.querySelectorAll(".day-tab").forEach((t, idx) => {
        t.classList.toggle("active", idx === i);
      });
      renderDayTimeline();
      updateMapLocation();
    });
    tabsContainer.appendChild(tab);
  }
}
function renderDayTimeline() {
  const container = document.getElementById("itinerary-timeline");
  container.innerHTML = "";
  
  const trip = trips.find(t => t.id === currentTripId);
  if (!trip) return;
  
  const dayActivities = trip.activities
    .filter(act => act.day === activeDayIndex)
    .sort((a, b) => a.time.localeCompare(b.time));
    
  if (dayActivities.length === 0) {
    container.innerHTML = `
      <div class="empty-itinerary">
        <div class="empty-icon">📍</div>
        <div class="empty-title">Nothing planned for Day ${activeDayIndex + 1}</div>
        <div class="empty-desc">Create details for sights to see, dining places, hotels, or custom activities.</div>
        <button class="btn btn-secondary" onclick="openActivityModal()">Add First Activity</button>
      </div>
    `;
    return;
  }
  
  dayActivities.forEach(act => {
    const card = document.createElement("div");
    card.className = "timeline-item";
    card.innerHTML = `
      <div class="timeline-dot"></div>
      <div class="glass-panel activity-card" onclick="panToActivity('${act.id}')" style="cursor: pointer;">
        <div class="activity-main">
          <div class="activity-time-badge">${act.time}</div>
          <div class="activity-details">
            <h4>${escapeHtml(act.name)}</h4>
            <p style="margin-bottom: 4px;">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: middle; margin-right: 4px;"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
              ${escapeHtml(act.location || "Location mapped")}
            </p>
            ${act.notes ? `<p style="font-size: 0.8rem; opacity: 0.8; font-style: italic;">"${escapeHtml(act.notes)}"</p>` : ''}
            <span class="activity-type-tag tag-${act.category}">${act.category}</span>
          </div>
        </div>
        <div class="activity-right">
          <div class="activity-cost">${Number(act.cost) === 0 ? 'Free' : `$${act.cost}`}</div>
          <div class="activity-actions">
            <button class="btn-action-icon btn-edit" onclick="event.stopPropagation(); editActivity('${act.id}')" title="Edit Activity">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
            </button>
            <button class="btn-action-icon btn-delete" onclick="event.stopPropagation(); deleteActivity('${act.id}')" title="Delete Activity">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
            </button>
          </div>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}
function renderBudgetStats() {
  const trip = trips.find(t => t.id === currentTripId);
  if (!trip) return;
  
  const totalCost = trip.activities.reduce((sum, act) => sum + Number(act.cost), 0);
  const budget = trip.budget;
  const percent = Math.min(Math.round((totalCost / budget) * 100), 100);
  const isOverBudget = totalCost > budget;
  
  const circleOffset = 376.99 - (percent / 100) * 376.99;
  const progressRing = document.getElementById("budget-progress-ring");
  
  if (progressRing) {
    progressRing.style.strokeDashoffset = circleOffset;
    progressRing.style.stroke = isOverBudget ? "var(--accent-rose)" : "url(#budget-grad)";
  }
  
  document.getElementById("budget-percent-text").innerText = `${percent}%`;
  document.getElementById("budget-total-val").innerText = `$${budget}`;
  document.getElementById("budget-spent-val").innerText = `$${totalCost}`;
  
  if (isOverBudget) {
    document.getElementById("budget-spent-val").style.color = "var(--accent-rose)";
    showToast("Warning: Budget limit exceeded!", "error");
  } else {
    document.getElementById("budget-spent-val").style.color = "var(--accent-cyan)";
  }
}
// ==========================================================================
// 8. PRE-TRIP CHECKLIST SYSTEM
// ==========================================================================
function renderChecklist() {
  const container = document.getElementById("checklist-container");
  container.innerHTML = "";
  
  const trip = trips.find(t => t.id === currentTripId);
  if (!trip) return;
  
  if (!trip.checklist || trip.checklist.length === 0) {
    container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.85rem; text-align: center;">No checklists chores created.</p>`;
    return;
  }
  
  trip.checklist.forEach(item => {
    const div = document.createElement("div");
    div.className = `checklist-item ${item.checked ? 'checked' : ''}`;
    div.innerHTML = `
      <input type="checkbox" ${item.checked ? 'checked' : ''} onchange="toggleTodoItem('${item.id}')">
      <span style="flex-grow: 1;">${escapeHtml(item.text)}</span>
      <button class="btn-action-icon btn-delete" onclick="deleteTodoItem('${item.id}')" style="opacity: 0.6; padding: 2px;" title="Remove Task">
        &times;
      </button>
    `;
    
    div.addEventListener("mouseenter", () => div.querySelector(".btn-delete").style.opacity = 1);
    div.addEventListener("mouseleave", () => div.querySelector(".btn-delete").style.opacity = 0.6);
    
    container.appendChild(div);
  });
}
async function addTodoItem() {
  const input = document.getElementById("new-todo-input");
  const val = input.value.trim();
  if (!val) return;
  
  const tripIndex = trips.findIndex(t => t.id === currentTripId);
  if (tripIndex === -1) return;
  
  if (!trips[tripIndex].checklist) {
    trips[tripIndex].checklist = [];
  }
  
  trips[tripIndex].checklist.push({
    id: `chk-${Date.now()}`,
    text: val,
    checked: false
  });
  
  saveTripsData();
  renderChecklist();
  input.value = "";
  
  showToast("Checklist chore added", "success");
  updateTripOnServer(currentTripId);
}
async function toggleTodoItem(itemId) {
  const tripIndex = trips.findIndex(t => t.id === currentTripId);
  if (tripIndex === -1) return;
  
  const item = trips[tripIndex].checklist.find(i => i.id === itemId);
  if (item) {
    item.checked = !item.checked;
    saveTripsData();
    renderChecklist();
    updateTripOnServer(currentTripId);
  }
}
async function deleteTodoItem(itemId) {
  const tripIndex = trips.findIndex(t => t.id === currentTripId);
  if (tripIndex === -1) return;
  
  trips[tripIndex].checklist = trips[tripIndex].checklist.filter(i => i.id !== itemId);
  saveTripsData();
  renderChecklist();
  
  showToast("Checklist chore deleted", "warning");
  updateTripOnServer(currentTripId);
}
// ==========================================================================
// 9. LEAFLET MAP INTEGRATION
// ==========================================================================
function initMapIfNeeded() {
  if (map !== null) return;
  
  const trip = trips.find(t => t.id === currentTripId);
  const lat = trip ? trip.lat : 35.6762;
  const lng = trip ? trip.lng : 139.6503;
  
  try {
    map = L.map('map', {
      zoomControl: true,
      attributionControl: false
    }).setView([lat, lng], 12);
    
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 20
    }).addTo(map);
    
    document.getElementById("offline-map-banner").style.display = "none";
  } catch (err) {
    console.warn("Offline environment; skipping dynamic map layout.");
    document.getElementById("offline-map-banner").style.display = "flex";
  }
}
function updateMapLocation() {
  initMapIfNeeded();
  
  const trip = trips.find(t => t.id === currentTripId);
  if (!trip) return;
  
  const dayActivities = trip.activities
    .filter(act => act.day === activeDayIndex)
    .sort((a, b) => a.time.localeCompare(b.time));
    
  mapMarkers.forEach(m => {
    if (map) map.removeLayer(m);
  });
  mapMarkers = [];
  
  if (mapPolyline && map) {
    map.removeLayer(mapPolyline);
    mapPolyline = null;
  }
  
  const latLngs = [];
  
  if (map) {
    if (dayActivities.length === 0) {
      map.setView([trip.lat, trip.lng], 11);
      return;
    }
    
    dayActivities.forEach((act, idx) => {
      const position = [act.lat, act.lng];
      latLngs.push(position);
      
      const customIcon = L.divIcon({
        className: 'custom-div-icon',
        html: `<div>${idx + 1}</div>`,
        iconSize: [28, 28]
      });
      
      const marker = L.marker(position, { icon: customIcon })
        .addTo(map)
        .bindPopup(`
          <div style="font-family:'Outfit',sans-serif; color:var(--text-main);">
            <strong style="color:var(--accent-cyan); font-size:1rem;">${escapeHtml(act.name)}</strong><br/>
            <span style="font-size:0.85rem; opacity:0.8;">🕒 ${act.time}</span><br/>
            <span style="font-size:0.85rem;">💵 ${Number(act.cost) === 0 ? 'Free' : '$' + act.cost}</span>
          </div>
        `);
        
      marker.activityId = act.id;
      mapMarkers.push(marker);
    });
    
    if (latLngs.length > 1) {
      mapPolyline = L.polyline(latLngs, {
        color: '#7c3aed',
        weight: 3,
        opacity: 0.8,
        dashArray: '5, 10',
        lineJoin: 'round'
      }).addTo(map);
    }
    
    if (latLngs.length > 0) {
      const bounds = L.latLngBounds(latLngs);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }
}
function panToActivity(actId) {
  const marker = mapMarkers.find(m => m.activityId === actId);
  if (marker && map) {
    map.panTo(marker.getLatLng());
    marker.openPopup();
  }
}
// ==========================================================================
// 10. ACTIVITY CREATOR MODALS
// ==========================================================================
function openActivityModal() {
  document.getElementById("activity-modal-title").innerText = "Schedule Activity";
  document.getElementById("btn-activity-save").innerText = "Schedule";
  document.getElementById("edit-activity-id").value = "";
  document.getElementById("activity-form").reset();
  
  const now = new Date();
  const timeString = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
  document.getElementById("activity-time").value = timeString;
  
  document.querySelectorAll(".category-option").forEach(opt => opt.classList.remove("selected"));
  document.querySelector(".category-option[data-cat='sightseeing']").classList.add("selected");
  document.getElementById("activity-modal").classList.add("active");
}
function closeActivityModal() {
  document.getElementById("activity-modal").classList.remove("active");
}
function selectCatOption(element) {
  document.querySelectorAll(".category-option").forEach(opt => opt.classList.remove("selected"));
  element.classList.add("selected");
}
async function handleActivitySubmit(e) {
  e.preventDefault();
  const tripIndex = trips.findIndex(t => t.id === currentTripId);
  if (tripIndex === -1) return;
  
  const editId = document.getElementById("edit-activity-id").value;
  const name = document.getElementById("activity-name").value.trim();
  const time = document.getElementById("activity-time").value;
  const cost = Number(document.getElementById("activity-cost").value);
  const location = document.getElementById("activity-location").value.trim();
  const cat = document.querySelector(".category-option.selected").getAttribute("data-cat");
  const notes = document.getElementById("activity-notes").value.trim();
  
  if (editId) {
    // Edit existing activity
    const actIndex = trips[tripIndex].activities.findIndex(a => a.id === editId);
    if (actIndex !== -1) {
      const act = trips[tripIndex].activities[actIndex];
      act.name = name;
      act.time = time;
      act.cost = cost;
      act.category = cat;
      act.notes = notes;
      
      if (location !== act.location) {
        act.location = location;
        const offsetCoords = generateActivityCoords(trips[tripIndex], location);
        act.lat = offsetCoords[0];
        act.lng = offsetCoords[1];
      }
      showToast("Activity updated", "success");
    }
  } else {
    // Append new activity
    const offsetCoords = generateActivityCoords(trips[tripIndex], location);
    const newAct = {
      id: `act-${Date.now()}`,
      day: activeDayIndex,
      name: name,
      time: time,
      cost: cost,
      location: location,
      category: cat,
      notes: notes,
      lat: offsetCoords[0],
      lng: offsetCoords[1]
    };
    
    trips[tripIndex].activities.push(newAct);
    showToast("Activity scheduled", "success");
  }
  
  saveTripsData();
  closeActivityModal();
  
  renderDayTimeline();
  renderBudgetStats();
  updateMapLocation();
  
  // Sync to database
  updateTripOnServer(currentTripId);
}
function editActivity(actId) {
  const trip = trips.find(t => t.id === currentTripId);
  if (!trip) return;
  
  const act = trip.activities.find(a => a.id === actId);
  if (!act) return;
  
  document.getElementById("activity-modal-title").innerText = "Edit Activity Details";
  document.getElementById("btn-activity-save").innerText = "Save Changes";
  document.getElementById("edit-activity-id").value = act.id;
  
  document.getElementById("activity-name").value = act.name;
  document.getElementById("activity-time").value = act.time;
  document.getElementById("activity-cost").value = act.cost;
  document.getElementById("activity-location").value = act.location;
  document.getElementById("activity-notes").value = act.notes || "";
  
  document.querySelectorAll(".category-option").forEach(opt => {
    opt.classList.toggle("selected", opt.getAttribute("data-cat") === act.category);
  });
  
  document.getElementById("activity-modal").classList.add("active");
}
async function deleteActivity(actId) {
  if (confirm("Delete this activity?")) {
    const tripIndex = trips.findIndex(t => t.id === currentTripId);
    if (tripIndex !== -1) {
      trips[tripIndex].activities = trips[tripIndex].activities.filter(a => a.id !== actId);
      saveTripsData();
      
      renderDayTimeline();
      renderBudgetStats();
      updateMapLocation();
      showToast("Activity removed", "warning");
      
      updateTripOnServer(currentTripId);
    }
  }
}
function generateActivityCoords(trip, locationName) {
  let hash = 0;
  for (let i = 0; i < locationName.length; i++) {
    hash = locationName.charCodeAt(i) + ((hash << 5) - hash);
  }
  const latOffset = ((hash % 100) / 1000) * 0.4;
  const lngOffset = (((hash >> 2) % 100) / 1000) * 0.4;
  return [trip.lat + latOffset, trip.lng + lngOffset];
}
// ==========================================================================
// 11. LOCAL DESTINATION MINI GALLERY
// ==========================================================================
function renderLocalGallery(destination) {
  const grid = document.getElementById("gallery-grid");
  grid.innerHTML = "";
  const destLower = destination.toLowerCase();
  let imgUrls = DESTINATION_GALLERY.default;
  
  if (destLower.includes("tokyo")) {
    imgUrls = DESTINATION_GALLERY.tokyo;
  } else if (destLower.includes("paris")) {
    imgUrls = DESTINATION_GALLERY.paris;
  }
  
  imgUrls.forEach(url => {
    const item = document.createElement("div");
    item.className = "gallery-item";
    item.style.backgroundImage = `url('${url}')`;
    item.title = `Spot in ${destination}`;
    grid.appendChild(item);
  });
}
// ==========================================================================
// 12. DATA IMPORT / EXPORT UTILITIES
// ==========================================================================
function exportTrip() {
  const trip = trips.find(t => t.id === currentTripId);
  if (!trip) return;
  const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(trip, null, 2));
  const dlAnchorElem = document.createElement('a');
  dlAnchorElem.setAttribute("href", dataStr);
  dlAnchorElem.setAttribute("download", `VibeVoyage_${trip.destination.replace(/[\s,]+/g, '_')}.json`);
  dlAnchorElem.click();
  showToast("Itinerary exported to JSON!", "success");
}
function triggerImport() {
  document.getElementById("trip-import-file").click();
}
// Set up import button inside dashboard header
const oldDashboardHeader = document.querySelector(".dashboard-header");
if (oldDashboardHeader) {
  const btnWrap = oldDashboardHeader.querySelector("button").parentElement;
  if (btnWrap && !document.getElementById("btn-import-itinerary")) {
    const importBtn = document.createElement("button");
    importBtn.id = "btn-import-itinerary";
    importBtn.className = "btn btn-secondary";
    importBtn.style.marginRight = "10px";
    importBtn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
      Import Trip
    `;
    importBtn.onclick = triggerImport;
    btnWrap.insertBefore(importBtn, btnWrap.firstChild);
  }
}
async function handleImportFile(e) {
  const file = e.target.files[0];
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = async function(event) {
    try {
      const importedTrip = JSON.parse(event.target.result);
      if (!importedTrip.destination || !importedTrip.startDate || !importedTrip.endDate || !Array.isArray(importedTrip.activities)) {
        showToast("Invalid travel planner file format.", "error");
        return;
      }
      
      importedTrip.id = "trip-" + Date.now();
      trips.push(importedTrip);
      
      // Upload to server
      const success = await createTripOnServer(importedTrip);
      
      if (!success) {
        saveTripsData();
        renderTripsList();
        showToast(`Imported trip to ${importedTrip.destination} locally`, "warning");
      }
    } catch (err) {
      showToast("Error parsing file JSON.", "error");
    }
  };
  reader.readAsText(file);
}
// ==========================================================================
// 13. HELPER UTILITIES
// ==========================================================================
function getMockCoords(destName) {
  let hash = 0;
  for (let i = 0; i < destName.length; i++) {
    hash = destName.charCodeAt(i) + ((hash << 5) - hash);
  }
  const lat = 20 + (Math.abs(hash % 3000) / 100);
  const lng = -10 + (Math.abs((hash >> 3) % 15000) / 100);
  return [lat, lng];
}
function getDaysCount(start, end) {
  const sDate = new Date(start);
  const eDate = new Date(end);
  const diffTime = Math.abs(eDate - sDate);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
  return diffDays || 1;
}
function formatDate(dateStr) {
  const options = { month: 'short', day: 'numeric', year: 'numeric' };
  return new Date(dateStr).toLocaleDateString('en-US', options);
}
function escapeHtml(unsafe) {
  if (!unsafe) return "";
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  let icon = "✓";
  if (type === "error") icon = "✕";
  if (type === "warning") icon = "⚠️";
  
  toast.innerHTML = `
    <span style="font-size: 1.1rem;">${icon}</span>
    <span>${message}</span>
  `;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add("toast-out");
    toast.addEventListener("animationend", () => {
      toast.remove();
    });
  }, 3500);
}
