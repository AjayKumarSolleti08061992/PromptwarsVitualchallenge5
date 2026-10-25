/**
 * Cloudflare Worker for Google Cloud Technologies Summit 2026 & AI Planner
 * High-performance edge router with defense-in-depth security, caching,
 * schedule API, and Gemini AI plan generation.
 */

const SECURITY_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Content-Security-Policy":
    "default-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://fonts.gstatic.com; img-src 'self' data: https:; font-src https://fonts.gstatic.com;",
};

// Google Cloud Technologies Summit Schedule Data
const EVENTS_DATA = [
  {
    id: "T1",
    title: "Scaling Applications with Google Kubernetes Engine",
    speakers: [
      { first_name: "Alice", last_name: "Chen", linkedin: "https://linkedin.com/in/alicechen" },
      { first_name: "Bob", last_name: "Smith", linkedin: "https://linkedin.com/in/bobsmith" },
    ],
    category: "1",
    category_name: "Infrastructure & Compute",
    description: "Learn how to autoscale your microservices efficiently using GKE.",
    time: "09:00 - 09:45",
    type: "talk",
  },
  {
    id: "T2",
    title: "Serverless Architectures with Cloud Run",
    speakers: [
      { first_name: "Charlie", last_name: "Davis", linkedin: "https://linkedin.com/in/charliedavis" },
    ],
    category: "1",
    category_name: "Infrastructure & Compute",
    description: "Deploy highly scalable containerized applications on fully managed serverless platforms.",
    time: "10:00 - 10:45",
    type: "talk",
  },
  {
    id: "T3",
    title: "Introduction to Vertex AI",
    speakers: [
      { first_name: "Diana", last_name: "Evans", linkedin: "https://linkedin.com/in/dianaevans" },
    ],
    category: "2",
    category_name: "Data & AI",
    description: "A comprehensive guide to building, deploying, and scaling machine learning models with Vertex AI.",
    time: "11:00 - 11:45",
    type: "talk",
  },
  {
    id: "T4",
    title: "Data Engineering with BigQuery",
    speakers: [
      { first_name: "Eve", last_name: "Foster", linkedin: "https://linkedin.com/in/evefoster" },
      { first_name: "Frank", last_name: "Green", linkedin: "https://linkedin.com/in/frankgreen" },
    ],
    category: "2",
    category_name: "Data & AI",
    description: "Best practices for data modeling and querying petabytes of data using BigQuery.",
    time: "12:00 - 12:45",
    type: "talk",
  },
  {
    id: "L1",
    title: "Lunch Break",
    speakers: [],
    category: "",
    category_name: "Break",
    description: "Networking lunch in the main hall. Enjoy a 60-minute break.",
    time: "12:45 - 13:45",
    type: "break",
  },
  {
    id: "T5",
    title: "Modernizing Legacy Apps with Anthos",
    speakers: [
      { first_name: "Grace", last_name: "Hopper", linkedin: "https://linkedin.com/in/gracehopper" },
    ],
    category: "1",
    category_name: "Infrastructure & Compute",
    description: "Strategies for modernizing existing infrastructure using Google Cloud Anthos across multi-cloud environments.",
    time: "14:00 - 14:45",
    type: "talk",
  },
  {
    id: "T6",
    title: "Real-time Streaming with Dataflow",
    speakers: [
      { first_name: "Hank", last_name: "Irving", linkedin: "https://linkedin.com/in/hankirving" },
    ],
    category: "2",
    category_name: "Data & AI",
    description: "Building unified stream and batch data processing pipelines with Cloud Dataflow.",
    time: "15:00 - 15:45",
    type: "talk",
  },
  {
    id: "T7",
    title: "Securing Your Cloud Infrastructure",
    speakers: [
      { first_name: "Ivy", last_name: "Johnson", linkedin: "https://linkedin.com/in/ivyjohnson" },
      { first_name: "Jack", last_name: "King", linkedin: "https://linkedin.com/in/jackking" },
    ],
    category: "1",
    category_name: "Infrastructure & Compute",
    description: "Deep dive into IAM, VPC security, and zero-trust security models on Google Cloud.",
    time: "16:00 - 16:45",
    type: "talk",
  },
  {
    id: "T8",
    title: "Generative AI and Large Language Models on GCP",
    speakers: [
      { first_name: "Karen", last_name: "Lee", linkedin: "https://linkedin.com/in/karenlee" },
    ],
    category: "2",
    category_name: "Data & AI",
    description: "Harnessing the power of generative AI and prompt engineering directly on Google Cloud.",
    time: "17:00 - 17:45",
    type: "talk",
  },
];

/**
 * Fast structured event plan generator
 */
function generateStructuredPlan(eventType, date, budget, attendees, selectedIds) {
  const b = Number(budget) || 10000;
  const att = Number(attendees) || 100;
  const dateStr = date ? `on ${date}` : "October 25, 2026";
  const venueCost = Math.round(b * 0.4);
  const cateringCost = Math.round(b * 0.3);
  const decorCost = Math.round(b * 0.15);
  const bufferCost = Math.round(b * 0.15);

  let eventsList = EVENTS_DATA;
  if (selectedIds && Array.isArray(selectedIds) && selectedIds.length > 0) {
    eventsList = EVENTS_DATA.filter((e) => selectedIds.includes(e.id));
  }

  const sessionHighlights = eventsList
    .map((e) => `- **${e.time}**: ${e.title} (${e.category_name || e.type})`)
    .join("\n");

  return `# 🚀 Conference & Event Plan: ${eventType.toUpperCase()}
**Date:** ${dateStr} | **Target Attendees:** ${att.toLocaleString()} | **Total Budget:** $${b.toLocaleString()}

---

### ⏱️ Recommended Session Schedule
${sessionHighlights}

---

### 💰 Strategic Budget Allocation Breakdown
- **Venue & Audio/Visual Technology (40%):** $${venueCost.toLocaleString()}
- **Catering, Refreshments & Hospitality (30%):** $${cateringCost.toLocaleString()}
- **Event Materials, Badges & Branding (15%):** $${decorCost.toLocaleString()}
- **Contingency Reserve & Speaker Stipends (15%):** $${bufferCost.toLocaleString()}

---

### 💡 High-Impact Attendee Experience Ideas
1. **Interactive Demo Pods:** Hands-on developer labs featuring Vertex AI, Gemini, and Cloud Run templates.
2. **Keynote Live Q&A:** Digital interactive polling and attendee networking lounges.
3. **Attendee Swag & Certifications:** Google Cloud credential vouchers and developer welcome packs.
`;
}

/**
 * Call Google Generative AI (Gemini) with fast 5-second timeout
 */
async function callGeminiAI(eventType, date, budget, apiKey) {
  const prompt = `You are an expert technical conference and event planner. Create a concise, actionable plan for a ${eventType} ${
    date ? `on date ${date}` : ""
  } with a total budget of $${budget}.
Include:
1. Timeline (Pre-event milestones, Event day schedule, Post-event wrap-up)
2. Budget breakdown based on total $${budget}
3. Recommended vendor & logistics priorities
4. 3-4 creative ideas to make this event memorable and unique.

Format in clean Markdown with headers and bullet points.`;

  const model = "gemini-2.5-flash-lite";
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
      }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (res.ok) {
      const data = await res.json();
      const candidate = data?.candidates?.[0]?.content?.parts?.[0]?.text;
      if (candidate) return candidate.trim();
    }
  } catch (err) {
    console.warn("Gemini call timed out or failed:", err.message);
  }

  return null;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 1. CORS Preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: SECURITY_HEADERS });
    }

    // 2. GET /api/schedule -> Returns Conference Agenda JSON with caching
    if (url.pathname === "/api/schedule" && request.method === "GET") {
      return new Response(JSON.stringify(EVENTS_DATA), {
        status: 200,
        headers: {
          ...SECURITY_HEADERS,
          "Content-Type": "application/json",
          "Cache-Control": "public, max-age=3600, s-maxage=86400",
        },
      });
    }

    // 3. POST /api/generate_plan -> Conference Itinerary & Budget Generator
    if (url.pathname === "/api/generate_plan" && request.method === "POST") {
      try {
        const body = await request.json().catch(() => ({}));
        const budget = Number(body.budget || body.budget_usd || 10000);
        const attendees = Number(body.attendees || 100);
        const eventType = body.event_type || "Google Cloud Technical Summit";
        const eventDate = body.event_date || "2026-10-25";
        const eventIds = body.event_ids || [];

        // Input validation
        if (budget < 0 || budget > 100000000) {
          return new Response(JSON.stringify({ error: "Invalid budget range." }), {
            status: 400,
            headers: { ...SECURITY_HEADERS, "Content-Type": "application/json" },
          });
        }

        const plan = generateStructuredPlan(eventType, eventDate, budget, attendees, eventIds);
        const summary = {
          total_events: eventIds.length > 0 ? eventIds.length : EVENTS_DATA.length,
          estimated_hours: 6.5,
          budget_suggestion: `Allocate ~$${(budget / Math.max(eventIds.length || 8, 1)).toFixed(2)} per track.`,
          venue_hint: `Optimized for ${attendees} participants.`,
        };

        return new Response(JSON.stringify({ plan, summary }), {
          status: 200,
          headers: { ...SECURITY_HEADERS, "Content-Type": "application/json" },
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message || "Server Error" }), {
          status: 500,
          headers: { ...SECURITY_HEADERS, "Content-Type": "application/json" },
        });
      }
    }

    // 4. POST /generate and POST /api/generate -> General AI Plan Generator
    if (
      (url.pathname === "/generate" || url.pathname === "/api/generate") &&
      request.method === "POST"
    ) {
      try {
        const body = await request.json().catch(() => ({}));
        const eventType = body.event_type || body.type || "Conference";
        const eventDate = body.event_date || body.date || "";
        const budget = Number(body.budget_usd || body.budget || 5000);
        const attendees = Number(body.attendees || 100);

        if (budget < 0 || budget > 100000000) {
          return new Response(JSON.stringify({ error: "Invalid budget amount." }), {
            status: 400,
            headers: { ...SECURITY_HEADERS, "Content-Type": "application/json" },
          });
        }

        const apiKey = env.GEMMA_API_KEY || "";
        let plan = null;

        if (apiKey) {
          plan = await callGeminiAI(eventType, eventDate, budget, apiKey);
        }

        if (!plan) {
          plan = generateStructuredPlan(eventType, eventDate, budget, attendees, body.event_ids);
        }

        return new Response(JSON.stringify({ plan }), {
          status: 200,
          headers: { ...SECURITY_HEADERS, "Content-Type": "application/json" },
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message || "Failed to generate plan" }), {
          status: 500,
          headers: { ...SECURITY_HEADERS, "Content-Type": "application/json" },
        });
      }
    }

    // 5. Serve static assets via Cloudflare Assets
    if (env.ASSETS) {
      return env.ASSETS.fetch(request);
    }

    return new Response("Not found", { status: 404, headers: SECURITY_HEADERS });
  },
};
