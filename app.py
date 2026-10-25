"""Google Cloud Technologies Summit 2026 - Conference Server & API.

This module provides the Flask application for displaying technical conference
schedules, filtering sessions by category, and generating customized event
itineraries with budget allocation and AI assistance.
"""

from datetime import datetime
import os
from typing import Any, Dict, List, Optional, Tuple, Union
from flask import Flask, jsonify, render_template, request, Response

app = Flask(__name__)

# Security configuration
app.config["JSON_SORT_KEYS"] = False
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024  # 1 MB maximum request size

# Conference Events Data (Google Cloud Technologies Summit)
EVENTS_DATA: List[Dict[str, Any]] = [
    {
        "id": "T1",
        "title": "Scaling Applications with Google Kubernetes Engine",
        "speakers": [
            {
                "first_name": "Alice",
                "last_name": "Chen",
                "linkedin": "https://linkedin.com/in/alicechen",
            },
            {
                "first_name": "Bob",
                "last_name": "Smith",
                "linkedin": "https://linkedin.com/in/bobsmith",
            },
        ],
        "category": "1",
        "category_name": "Infrastructure & Compute",
        "description": "Learn how to autoscale your microservices efficiently using GKE.",
        "time": "09:00 - 09:45",
        "type": "talk",
    },
    {
        "id": "T2",
        "title": "Serverless Architectures with Cloud Run",
        "speakers": [
            {
                "first_name": "Charlie",
                "last_name": "Davis",
                "linkedin": "https://linkedin.com/in/charliedavis",
            }
        ],
        "category": "1",
        "category_name": "Infrastructure & Compute",
        "description": "Deploy highly scalable containerized applications on fully managed serverless platforms.",
        "time": "10:00 - 10:45",
        "type": "talk",
    },
    {
        "id": "T3",
        "title": "Introduction to Vertex AI",
        "speakers": [
            {
                "first_name": "Diana",
                "last_name": "Evans",
                "linkedin": "https://linkedin.com/in/dianaevans",
            }
        ],
        "category": "2",
        "category_name": "Data & AI",
        "description": "A comprehensive guide to building, deploying, and scaling machine learning models with Vertex AI.",
        "time": "11:00 - 11:45",
        "type": "talk",
    },
    {
        "id": "T4",
        "title": "Data Engineering with BigQuery",
        "speakers": [
            {
                "first_name": "Eve",
                "last_name": "Foster",
                "linkedin": "https://linkedin.com/in/evefoster",
            },
            {
                "first_name": "Frank",
                "last_name": "Green",
                "linkedin": "https://linkedin.com/in/frankgreen",
            },
        ],
        "category": "2",
        "category_name": "Data & AI",
        "description": "Best practices for data modeling and querying petabytes of data using BigQuery.",
        "time": "12:00 - 12:45",
        "type": "talk",
    },
    {
        "id": "L1",
        "title": "Lunch Break",
        "speakers": [],
        "category": "",
        "category_name": "Break",
        "description": "Networking lunch in the main hall. Enjoy a 60-minute break.",
        "time": "12:45 - 13:45",
        "type": "break",
    },
    {
        "id": "T5",
        "title": "Modernizing Legacy Apps with Anthos",
        "speakers": [
            {
                "first_name": "Grace",
                "last_name": "Hopper",
                "linkedin": "https://linkedin.com/in/gracehopper",
            }
        ],
        "category": "1",
        "category_name": "Infrastructure & Compute",
        "description": "Strategies for modernizing existing infrastructure using Google Cloud Anthos across multi-cloud environments.",
        "time": "14:00 - 14:45",
        "type": "talk",
    },
    {
        "id": "T6",
        "title": "Real-time Streaming with Dataflow",
        "speakers": [
            {
                "first_name": "Hank",
                "last_name": "Irving",
                "linkedin": "https://linkedin.com/in/hankirving",
            }
        ],
        "category": "2",
        "category_name": "Data & AI",
        "description": "Building unified stream and batch data processing pipelines with Cloud Dataflow.",
        "time": "15:00 - 15:45",
        "type": "talk",
    },
    {
        "id": "T7",
        "title": "Securing Your Cloud Infrastructure",
        "speakers": [
            {
                "first_name": "Ivy",
                "last_name": "Johnson",
                "linkedin": "https://linkedin.com/in/ivyjohnson",
            },
            {
                "first_name": "Jack",
                "last_name": "King",
                "linkedin": "https://linkedin.com/in/jackking",
            },
        ],
        "category": "1",
        "category_name": "Infrastructure & Compute",
        "description": "Deep dive into IAM, VPC security, and zero-trust security models on Google Cloud.",
        "time": "16:00 - 16:45",
        "type": "talk",
    },
    {
        "id": "T8",
        "title": "Generative AI and Large Language Models on GCP",
        "speakers": [
            {
                "first_name": "Karen",
                "last_name": "Lee",
                "linkedin": "https://linkedin.com/in/karenlee",
            }
        ],
        "category": "2",
        "category_name": "Data & AI",
        "description": "Harnessing the power of generative AI and prompt engineering directly on Google Cloud.",
        "time": "17:00 - 17:45",
        "type": "talk",
    },
]

CONFERENCE_INFO: Dict[str, str] = {
    "name": "Google Cloud Technologies Summit 2026",
    "date": datetime.now().strftime("%B %d, %Y"),
    "location": "Google Event Center, Mountain View, CA",
}


@app.after_request
def apply_security_headers(response: Response) -> Response:
    """Attach enterprise-grade security and caching headers to all responses.

    Args:
        response: The outgoing Flask Response object.

    Returns:
        The response with security headers attached.
    """
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' 'unsafe-inline' https://fonts.googleapis.com "
        "https://fonts.gstatic.com; img-src 'self' data: https:; "
        "font-src https://fonts.gstatic.com; connect-src 'self';"
    )
    return response


@app.route("/")
def index() -> str:
    """Render the main conference schedule and AI event planner page.

    Returns:
        Rendered HTML template.
    """
    return render_template("index.html", info=CONFERENCE_INFO)


@app.route("/api/schedule", methods=["GET"])
def schedule() -> Response:
    """Return the conference schedule data.

    Includes Cache-Control headers for optimal delivery performance.

    Returns:
        JSON response containing the list of conference talks and breaks.
    """
    resp = jsonify(EVENTS_DATA)
    resp.headers["Cache-Control"] = "public, max-age=3600, s-maxage=86400"
    return resp


def validate_plan_payload(
    data: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """Validate user inputs to prevent security injection and resource exhaustion.

    Args:
        data: The incoming dictionary payload.

    Returns:
        Tuple of (is_valid, error_message).
    """
    budget = data.get("budget", data.get("budget_usd"))
    if budget is not None:
        try:
            budget_val = float(budget)
            if budget_val < 0 or budget_val > 100_000_000:
                return False, "Budget must be between 0 and 100,000,000 USD."
        except (ValueError, TypeError):
            return False, "Budget must be a valid numeric amount."

    attendees = data.get("attendees")
    if attendees is not None:
        try:
            att_val = int(attendees)
            if att_val < 0 or att_val > 1_000_000:
                return False, "Attendees count must be between 0 and 1,000,000."
        except (ValueError, TypeError):
            return False, "Attendees must be a valid integer."

    return True, None


@app.route("/api/generate_plan", methods=["POST"])
def api_generate_plan() -> Union[Response, Tuple[Response, int]]:
    """Generate a conference itinerary and budget plan based on selected sessions.

    Expected JSON payload:
        {
            "event_ids": ["T1", "T3"],   // optional list of session IDs
            "budget": 5000,              // optional budget in USD
            "attendees": 50              // optional attendee count
        }

    Returns:
        JSON containing textual plan and metadata summary.
    """
    data = request.get_json(silent=True) or {}
    is_valid, err_msg = validate_plan_payload(data)
    if not is_valid:
        return jsonify({"error": err_msg}), 400

    selected_ids = data.get("event_ids")
    budget = data.get("budget")
    attendees = data.get("attendees")

    # Filter events matching selected IDs or default to all events
    if selected_ids and isinstance(selected_ids, list):
        selected = [e for e in EVENTS_DATA if e["id"] in selected_ids]
    else:
        selected = EVENTS_DATA

    plan_lines: List[str] = [
        f"# 📅 Itinerary: {CONFERENCE_INFO['name']}",
        f"**Date:** {CONFERENCE_INFO['date']} | **Location:** {CONFERENCE_INFO['location']}",
        "",
        "### ⏱️ Scheduled Sessions & Keynotes",
    ]

    total_time = 0.0
    for ev in selected:
        plan_lines.append(f"- **{ev['time']}**: {ev['title']} ({ev['category_name'] or ev['type'].title()})")
        try:
            start_str, end_str = ev["time"].split(" - ")
            h1, m1 = map(int, start_str.split(":"))
            h2, m2 = map(int, end_str.split(":"))
            total_time += (h2 - h1) + (m2 - m1) / 60.0
        except Exception:
            pass

    plan_lines.append("")
    plan_lines.append("### 💡 Recommended Preparation & Networking")
    plan_lines.append("- Arrive 15 minutes before the first talk for badge collection.")
    plan_lines.append("- Explore the interactive Vertex AI and GKE developer booths in the main hall.")

    summary: Dict[str, Any] = {
        "total_events": len(selected),
        "estimated_hours": round(total_time, 2),
    }

    if budget is not None:
        try:
            b_float = float(budget)
            per_event = round(b_float / max(len(selected), 1), 2)
            summary["budget_suggestion"] = f"Allocate ~${per_event:.2f} per session/track."
        except Exception:
            pass

    if attendees is not None:
        summary["venue_hint"] = f"Recommended room capacity: {attendees} participants."

    return jsonify({"plan": "\n".join(plan_lines), "summary": summary})


@app.route("/generate", methods=["POST"])
@app.route("/api/generate", methods=["POST"])
def generate() -> Union[Response, Tuple[Response, int]]:
    """Legacy and general AI event planning endpoint.

    Expects JSON body with keys: event_type, event_date, budget_usd.

    Returns:
        JSON with a 'plan' string field.
    """
    data = request.get_json(silent=True) or {}
    is_valid, err_msg = validate_plan_payload(data)
    if not is_valid:
        return jsonify({"error": err_msg}), 400

    event_type = data.get("event_type", data.get("type", "Conference"))
    budget = float(data.get("budget_usd", data.get("budget", 5000)) or 5000)
    event_date = data.get("event_date", data.get("date", CONFERENCE_INFO["date"]))

    plan = (
        f"# 🎉 Event Plan: {event_type.upper()}\n"
        f"**Date:** {event_date} | **Budget:** ${budget:,.2f}\n\n"
        f"### ⏱️ Timeline\n"
        f"- **Pre-Event (4 weeks):** Finalize venue and registrations.\n"
        f"- **Event Day:** Keynotes, technical breakouts, networking.\n"
        f"- **Post-Event:** Distribute slide decks and session recordings.\n\n"
        f"### 💰 Budget Allocation\n"
        f"- **Venue & AV (40%):** ${budget * 0.4:,.2f}\n"
        f"- **Catering & Hospitality (30%):** ${budget * 0.3:,.2f}\n"
        f"- **Materials & Logistics (15%):** ${budget * 0.15:,.2f}\n"
        f"- **Contingency (15%):** ${budget * 0.15:,.2f}\n"
    )

    return jsonify({"plan": plan})


if __name__ == "__main__":
    is_debug = os.getenv("FLASK_DEBUG", "0") == "1"
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=is_debug)
