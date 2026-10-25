// script.js – Handles form submission and calls the backend API to generate an event plan
// The front‑end expects a JSON response with a "plan" field containing markdown/text.

const API_ENDPOINT = "/generate"; // Cloudflare Worker / API endpoint

/**
 * Sends a request to the inference service.
 * @param {Object} payload - The request payload containing event details.
 * @returns {Promise<string>} The generated plan text.
 */
async function generatePlan(payload) {
    try {
        const response = await fetch(API_ENDPOINT, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            // Try fallback endpoint /api/generate if /generate returned 404
            if (response.status === 404) {
                const altResponse = await fetch("/api/generate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload),
                });
                if (altResponse.ok) {
                    const altData = await altResponse.json();
                    return altData.plan || "";
                }
            }
            throw new Error(`Server responded with ${response.status}`);
        }
        const data = await response.json();
        return data.plan || "";
    } catch (error) {
        console.error("Error generating plan:", error);
        return "Failed to generate plan. Please try again later.";
    }
}

/**
 * Formats the user input into the payload expected by the backend.
 * @param {string} type
 * @param {string} date
 * @param {number} budget
 * @returns {Object}
 */
function buildPayload(type, date, budget) {
    return {
        event_type: type,
        event_date: date,
        budget_usd: budget,
    };
}

/**
 * Handles the form submission, calls the API, and displays the result.
 */
async function handleSubmit(event) {
    event.preventDefault();
    const submitBtn = event.target.querySelector("button[type='submit']");
    const originalBtnText = submitBtn ? submitBtn.textContent : "Generate Plan";

    const type = document.getElementById("eventType").value;
    const date = document.getElementById("eventDate").value;
    const budget = Number(document.getElementById("budget").value);

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "⏳ Generating AI Plan...";
    }

    try {
        const payload = buildPayload(type, date, budget);
        const plan = await generatePlan(payload);

        const outputDiv = document.getElementById("planOutput");
        outputDiv.textContent = plan;
        document.getElementById("outputSection").style.display = "block";
        document.getElementById("outputSection").scrollIntoView({ behavior: "smooth" });
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = originalBtnText;
        }
    }
}

// Attach event listener after DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("planForm");
    if (form) {
        form.addEventListener("submit", handleSubmit);
    }
});
