// script.js – Handles form submission and calls the Gemma API to generate an event plan
// The front‑end expects a JSON response with a "plan" field containing markdown/text.
// Adjust the API_ENDPOINT to point to your backend that wraps the Gemma model.

const API_ENDPOINT = "/api/generate"; // Vercel serverless function endpoint

/**
 * Sends a request to the Gemma inference service.
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
        // You can extend the payload with additional fields such as location, guests, etc.
    };
}

/**
 * Handles the form submission, calls the API, and displays the result.
 */
async function handleSubmit(event) {
    event.preventDefault();
    const type = document.getElementById("eventType").value;
    const date = document.getElementById("eventDate").value;
    const budget = Number(document.getElementById("budget").value);

    const payload = buildPayload(type, date, budget);
    const plan = await generatePlan(payload);

    const outputDiv = document.getElementById("planOutput");
    outputDiv.textContent = plan;
    document.getElementById("outputSection").style.display = "block";
}

// Attach event listener after DOM is ready
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("planForm");
    form.addEventListener("submit", handleSubmit);
});
