from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os

app = Flask(__name__)

# Dummy Data for Google Cloud Technologies Conference
# Categories: 1: Infrastructure & Compute, 2: Data & AI
events_data = [
    {
        "id": "T1",
        "title": "Scaling Applications with Google Kubernetes Engine",
        "speakers": [
            {"first_name": "Alice", "last_name": "Chen", "linkedin": "https://linkedin.com/in/alicechen"},
            {"first_name": "Bob", "last_name": "Smith", "linkedin": "https://linkedin.com/in/bobsmith"}
        ],
        "category": "1",
        "category_name": "Infrastructure & Compute",
        "description": "Learn how to autoscale your microservices efficiently using GKE.",
        "time": "09:00 - 09:45",
        "type": "talk"
    },
    {
        "id": "T2",
        "title": "Serverless Architectures with Cloud Run",
        "speakers": [
            {"first_name": "Charlie", "last_name": "Davis", "linkedin": "https://linkedin.com/in/charliedavis"}
        ],
        "category": "1",
        "category_name": "Infrastructure & Compute",
        "description": "Deploy highly scalable containerized applications on fully managed serverless platforms.",
        "time": "10:00 - 10:45",
        "type": "talk"
    },
    {
        "id": "T3",
        "title": "Introduction to Vertex AI",
        "speakers": [
            {"first_name": "Diana", "last_name": "Evans", "linkedin": "https://linkedin.com/in/dianaevans"}
        ],
        "category": "2",
        "category_name": "Data & AI",
        "description": "A comprehensive guide to building, deploying, and scaling machine learning models with Vertex AI.",
        "time": "11:00 - 11:45",
        "type": "talk"
    },
    {
        "id": "T4",
        "title": "Data Engineering with BigQuery",
        "speakers": [
            {"first_name": "Eve", "last_name": "Foster", "linkedin": "https://linkedin.com/in/evefoster"},
            {"first_name": "Frank", "last_name": "Green", "linkedin": "https://linkedin.com/in/frankgreen"}
        ],
        "category": "2",
        "category_name": "Data & AI",
        "description": "Best practices for data modeling and querying petabytes of data using BigQuery.",
        "time": "12:00 - 12:45",
        "type": "talk"
    },
    {
        "id": "L1",
        "title": "Lunch Break",
        "speakers": [],
        "category": "",
        "category_name": "Break",
        "description": "Networking lunch in the main hall. Enjoy a 60-minute break.",
        "time": "12:45 - 13:45",
        "type": "break"
    },
    {
        "id": "T5",
        "title": "Modernizing Legacy Apps with Anthos",
        "speakers": [
            {"first_name": "Grace", "last_name": "Hopper", "linkedin": "https://linkedin.com/in/gracehopper"}
        ],
        "category": "1",
        "category_name": "Infrastructure & Compute",
        "description": "Strategies for modernizing existing infrastructure using Google Cloud Anthos across multi-cloud environments.",
        "time": "14:00 - 14:45",
        "type": "talk"
    },
    {
        "id": "T6",
        "title": "Real-time Streaming with Dataflow",
        "speakers": [
            {"first_name": "Hank", "last_name": "Irving", "linkedin": "https://linkedin.com/in/hankirving"}
        ],
        "category": "2",
        "category_name": "Data & AI",
        "description": "Building unified stream and batch data processing pipelines with Cloud Dataflow.",
        "time": "15:00 - 15:45",
        "type": "talk"
    },
    {
        "id": "T7",
        "title": "Securing Your Cloud Infrastructure",
        "speakers": [
            {"first_name": "Ivy", "last_name": "Johnson", "linkedin": "https://linkedin.com/in/ivyjohnson"},
            {"first_name": "Jack", "last_name": "King", "linkedin": "https://linkedin.com/in/jackking"}
        ],
        "category": "1",
        "category_name": "Infrastructure & Compute",
        "description": "Deep dive into IAM, VPC security, and zero-trust security models on Google Cloud.",
        "time": "16:00 - 16:45",
        "type": "talk"
    },
    {
        "id": "T8",
        "title": "Generative AI and Large Language Models on GCP",
        "speakers": [
            {"first_name": "Karen", "last_name": "Lee", "linkedin": "https://linkedin.com/in/karenlee"}
        ],
        "category": "2",
        "category_name": "Data & AI",
        "description": "Harnessing the power of generative AI and prompt engineering directly on Google Cloud.",
        "time": "17:00 - 17:45",
        "type": "talk"
    }
]

conference_info = {
    "name": "Google Cloud Technologies Summit 2026",
    "date": datetime.now().strftime("%B %d, %Y"),
    "location": "Google Event Center, Mountain View, CA"
}

@app.route("/")
def index():
    return render_template("index.html", info=conference_info)

@app.route("/api/schedule")
def schedule():
    return jsonify(events_data)

def generate_plan():
    """
    Generate an event plan based on user input.
    Expected JSON payload:
        {
            "event_ids": ["T1", "T3"],   // optional, defaults to all events
            "budget": 5000,              // optional, used for simple suggestion
            "attendees": 50              // optional, used for venue size hint
        }
    Returns a JSON object with a textual plan and summary metadata.
    """
    data = request.get_json(silent=True) or {}
    selected_ids = data.get("event_ids")
    budget = data.get("budget")
    attendees = data.get("attendees")

    # Filter events
    if selected_ids:
        selected = [e for e in events_data if e["id"] in selected_ids]
    else:
        selected = events_data

    # Build simple textual plan
    plan_lines = []
    total_time = 0
    for ev in selected:
        plan_lines.append(f"{ev['time']}: {ev['title']} ({ev['type']})")
        try:
            start, end = ev["time"].split(" - ")
            h1, m1 = map(int, start.split(":"))
            h2, m2 = map(int, end.split(":"))
            total_time += (h2 - h1) + (m2 - m1) / 60
        except Exception:
            pass

    plan_text = "\n".join(plan_lines)
    summary = {
        "total_events": len(selected),
        "estimated_hours": round(total_time, 2)
    }
    if budget:
        summary["budget_suggestion"] = f"Allocate ~${budget/len(selected):.2f} per event."
    if attendees:
        summary["venue_hint"] = f"Suitable for {attendees} participants."

    return jsonify({"plan": plan_text, "summary": summary})

@app.route("/api/generate_plan", methods=["POST"])
def api_generate_plan():
    """Endpoint that wraps generate_plan."""
    return generate_plan()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
