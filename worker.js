/**
 * Cloudflare Worker for GenAI Event Planner
 * Handles static asset serving and /generate & /api/generate AI endpoints.
 */

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

/**
 * Fallback event plan generator if external API is unreachable or key is not configured.
 */
function generateFallbackPlan(eventType, date, budget) {
  const dateStr = date ? `on ${date}` : "in the upcoming months";
  const b = Number(budget) || 10000;
  const venueBudget = (b * 0.4).toFixed(0);
  const cateringBudget = (b * 0.3).toFixed(0);
  const decorBudget = (b * 0.15).toFixed(0);
  const bufferBudget = (b * 0.15).toFixed(0);

  return `# 🎉 Event Plan: ${eventType.toUpperCase()}
**Date:** ${dateStr}
**Total Budget:** $${b.toLocaleString()}

---

### ⏱️ Timeline & Milestones
- **8 Weeks Prior:** Finalize theme, book primary venue, and send save-the-dates.
- **4 Weeks Prior:** Confirm catering menu, finalize vendor contracts (photography, music/AV).
- **1 Week Prior:** Final headcount check, brief vendors on logistics and arrival times.
- **Event Day:** On-site setup 3 hours before start; run technical soundcheck; welcome guests.
- **Post-Event:** Send thank-you notes, settle vendor payments, gather photos.

---

### 💰 Budget Allocation Breakdown
- **Venue & Rentals (40%):** $${venueBudget}
- **Catering & Refreshments (30%):** $${cateringBudget}
- **Decor, Lighting & Ambiance (15%):** $${decorBudget}
- **Contingency & Photography (15%):** $${bufferBudget}

---

### 💡 Creative & Personalized Ideas
- **Interactive Experience:** Set up a live digital guestbook or Polaroid memory corner.
- **Customized Welcome:** Personal gift bags with themed keepsakes.
- **Eco-friendly Elements:** Digital invites and locally sourced catering options.
`;
}

/**
 * Call Google Generative AI (Gemini / Gemma) with the user prompt.
 */
async function callAI(eventType, date, budget, apiKey) {
  const prompt = `You are an expert event planner. Create a comprehensive, concise, actionable plan for a ${eventType} ${
    date ? `on date ${date}` : ""
  } with a total budget of $${budget}.
Include:
1. Timeline (Pre-event milestones, Event day schedule, Post-event wrap-up)
2. Budget breakdown based on total $${budget}
3. Recommended vendor categories & priorities
4. 3-4 creative ideas to make this event memorable and unique.

Format the response in clean, beautiful Markdown with headers and bullet points.`;

  const models = ["gemini-flash-latest", "gemini-2.5-flash-lite", "gemini-2.5-flash"];

  for (const model of models) {
    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
        }),
      });

      if (res.ok) {
        const data = await res.json();
        const candidate = data?.candidates?.[0]?.content?.parts?.[0]?.text;
        if (candidate) {
          return candidate.trim();
        }
      }
    } catch (e) {
      console.warn(`Attempt with model ${model} failed:`, e);
    }
  }

  // If external call failed or had no response, return our structured plan
  return generateFallbackPlan(eventType, date, budget);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Handle CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: CORS_HEADERS,
      });
    }

    // Match both /generate and /api/generate
    if (
      (url.pathname === "/generate" || url.pathname === "/api/generate") &&
      request.method === "POST"
    ) {
      try {
        const body = await request.json().catch(() => ({}));
        const eventType = body.event_type || body.type || "Special Event";
        const eventDate = body.event_date || body.date || "";
        const budget = body.budget_usd || body.budget || 5000;

        const apiKey = env.GEMMA_API_KEY || "";
        let plan;

        if (apiKey) {
          plan = await callAI(eventType, eventDate, budget, apiKey);
        } else {
          plan = generateFallbackPlan(eventType, eventDate, budget);
        }

        return new Response(
          JSON.stringify({ plan }),
          {
            status: 200,
            headers: {
              ...CORS_HEADERS,
              "Content-Type": "application/json",
            },
          }
        );
      } catch (err) {
        return new Response(
          JSON.stringify({ error: err.message || "Failed to generate plan" }),
          {
            status: 500,
            headers: {
              ...CORS_HEADERS,
              "Content-Type": "application/json",
            },
          }
        );
      }
    }

    // If static assets binding exists (Cloudflare Assets)
    if (env.ASSETS) {
      return env.ASSETS.fetch(request);
    }

    return new Response("Not found", { status: 404, headers: CORS_HEADERS });
  },
};
