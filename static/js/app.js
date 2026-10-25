/**
 * script.js – Client-side Controller for Google Cloud Summit Schedule & AI Planner
 * Features: Dynamic Schedule Loading, Real-time Search & Category Filtering,
 * Session Selection for Custom Tracks, Accessible Submissions, and AI Generation.
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const scheduleContainer = document.getElementById("scheduleContainer");
    const searchInput = document.getElementById("searchInput");
    const categoryFilter = document.getElementById("categoryFilter");
    const noResults = document.getElementById("noResults");
    const planForm = document.getElementById("planForm");
    const generateBtn = document.getElementById("generateBtn");
    const outputSection = document.getElementById("outputSection");
    const planOutput = document.getElementById("planOutput");
    const formEventDate = document.getElementById("formEventDate");
    const selectedBadge = document.getElementById("selectedSessionsBadge");

    // Set default date to today or upcoming
    if (formEventDate && !formEventDate.value) {
        formEventDate.value = new Date().toISOString().split("T")[0];
    }

    let eventsData = [];
    const selectedEventIds = new Set();

    /**
     * Update the visual badge showing selected sessions
     */
    function updateSelectedBadge() {
        if (!selectedBadge) return;
        const count = selectedEventIds.size;
        if (count > 0) {
            selectedBadge.textContent = `🎯 ${count} Session${count > 1 ? "s" : ""} Selected for Itinerary`;
            selectedBadge.classList.remove("hidden");
        } else {
            selectedBadge.textContent = "📋 All Sessions Included in Plan (or select individual sessions above)";
            selectedBadge.classList.remove("hidden");
        }
    }

    /**
     * Fetch schedule from backend API
     */
    async function fetchSchedule() {
        if (!scheduleContainer) return;
        try {
            const res = await fetch("/api/schedule");
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            eventsData = await res.json();
            renderSchedule(eventsData);
            updateSelectedBadge();
        } catch (err) {
            console.error("Failed to fetch schedule:", err);
            scheduleContainer.innerHTML = `
                <div class="no-results" role="alert">
                    <p>Unable to load schedule from server. Please refresh the page.</p>
                </div>
            `;
        }
    }

    /**
     * Render session cards into the schedule container
     */
    function renderSchedule(events) {
        if (!scheduleContainer) return;
        scheduleContainer.innerHTML = "";

        if (!events || events.length === 0) {
            if (noResults) noResults.classList.remove("hidden");
            return;
        } else {
            if (noResults) noResults.classList.add("hidden");
        }

        events.forEach((event) => {
            const card = document.createElement("div");
            card.className = `event-card ${event.type === "break" ? "break-type" : ""}`;

            // Category Class & Badge
            const catClass = event.category ? `cat-${event.category}` : "";
            let badgeHTML = "";
            if (event.category_name && event.type !== "break") {
                badgeHTML = `<div class="event-category-badge ${catClass}">${escapeHtml(event.category_name)}</div>`;
            }

            // Speakers HTML
            let speakersHTML = "";
            if (event.speakers && event.speakers.length > 0) {
                const speakersList = event.speakers.map((speaker) => {
                    const initials = `${speaker.first_name?.[0] || ""}${speaker.last_name?.[0] || ""}`;
                    const fullName = `${speaker.first_name || ""} ${speaker.last_name || ""}`.trim();
                    return `
                        <div class="speaker">
                            <div class="speaker-avatar" aria-hidden="true">${escapeHtml(initials)}</div>
                            <div class="speaker-info">
                                <a href="${escapeHtml(speaker.linkedin || "#")}" target="_blank" rel="noopener noreferrer">
                                    ${escapeHtml(fullName)}
                                </a>
                            </div>
                        </div>
                    `;
                }).join("");
                speakersHTML = `<div class="event-speakers">${speakersList}</div>`;
            }

            // Checkbox for selection (talks only)
            let selectHTML = "";
            if (event.type !== "break") {
                const isChecked = selectedEventIds.has(event.id) ? "checked" : "";
                selectHTML = `
                    <label class="session-select-label">
                        <input type="checkbox" class="session-checkbox" value="${event.id}" ${isChecked} />
                        <span>Add to Custom Track</span>
                    </label>
                `;
            }

            card.innerHTML = `
                <div class="event-time">${escapeHtml(event.time)}</div>
                <div class="event-content">
                    ${badgeHTML}
                    <h3 class="event-title">${escapeHtml(event.title)}</h3>
                    <p class="event-desc">${escapeHtml(event.description || "")}</p>
                    ${speakersHTML}
                    ${selectHTML}
                </div>
            `;

            // Checkbox event listener
            const checkbox = card.querySelector(".session-checkbox");
            if (checkbox) {
                checkbox.addEventListener("change", (e) => {
                    if (e.target.checked) {
                        selectedEventIds.add(event.id);
                    } else {
                        selectedEventIds.delete(event.id);
                    }
                    updateSelectedBadge();
                });
            }

            scheduleContainer.appendChild(card);
        });
    }

    /**
     * Real-time search and category filtering
     */
    function filterEvents() {
        if (!searchInput || !categoryFilter) return;
        const query = searchInput.value.toLowerCase().trim();
        const category = categoryFilter.value;

        const filtered = eventsData.filter((event) => {
            if (event.type === "break") {
                return category === "all" && query === "";
            }

            const matchCategory = category === "all" || String(event.category) === category;
            const matchTitle = (event.title || "").toLowerCase().includes(query);
            const matchSpeaker = (event.speakers || []).some((speaker) => {
                const fullName = `${speaker.first_name || ""} ${speaker.last_name || ""}`.toLowerCase();
                return fullName.includes(query);
            });

            return matchCategory && (matchTitle || matchSpeaker);
        });

        renderSchedule(filtered);
    }

    if (searchInput) searchInput.addEventListener("input", filterEvents);
    if (categoryFilter) categoryFilter.addEventListener("change", filterEvents);

    /**
     * Form submission for AI Plan Generation
     */
    if (planForm) {
        planForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const originalBtnText = generateBtn ? generateBtn.innerHTML : "Generate Plan";

            const eventType = document.getElementById("eventType")?.value || "Conference";
            const date = formEventDate?.value || "";
            const budget = Number(document.getElementById("budget")?.value || 0);
            const attendees = Number(document.getElementById("attendees")?.value || 0);

            // Collect selected event IDs
            const eventIds = Array.from(selectedEventIds);

            if (generateBtn) {
                generateBtn.disabled = true;
                generateBtn.innerHTML = `<span>⏳ Generating AI Plan...</span>`;
            }

            try {
                let planText = "";
                const response = await fetch("/api/generate_plan", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        event_type: eventType,
                        event_date: date,
                        budget: budget,
                        attendees: attendees,
                        event_ids: eventIds,
                    }),
                });

                if (response.ok) {
                    const data = await response.json();
                    planText = data.plan || "";
                } else {
                    // Fallback to /generate
                    const altRes = await fetch("/generate", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            event_type: eventType,
                            event_date: date,
                            budget_usd: budget,
                            attendees: attendees,
                            event_ids: eventIds,
                        }),
                    });
                    if (altRes.ok) {
                        const data = await altRes.json();
                        planText = data.plan || "";
                    } else {
                        throw new Error(`Server responded with ${altRes.status}`);
                    }
                }

                if (planOutput) planOutput.textContent = planText;
                if (outputSection) {
                    outputSection.classList.remove("hidden");
                    outputSection.scrollIntoView({ behavior: "smooth" });
                }
            } catch (err) {
                console.error("Plan generation error:", err);
                if (planOutput) {
                    planOutput.textContent = "Error generating plan. Please verify server connection and try again.";
                }
                if (outputSection) outputSection.classList.remove("hidden");
            } finally {
                if (generateBtn) {
                    generateBtn.disabled = false;
                    generateBtn.innerHTML = originalBtnText;
                }
            }
        });
    }

    /**
     * Helper to escape HTML characters for security
     */
    function escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Initial fetch of conference schedule
    fetchSchedule();
});
