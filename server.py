"""Flask backend server wrapping the Gemma open-source language model.

This server provides local inference endpoints for event planning
using gemma.cpp binaries without external cloud dependencies.
"""

import os
from pathlib import Path
import subprocess
from typing import Any, Dict, Tuple, Union
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# Security configuration
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

# Configuration paths - override via environment variables
GEMMA_EXEC = os.getenv("GEMMA_EXEC", "gemma")
MODEL_DIR = Path(os.getenv("MODEL_DIR", "models/gemma-2b"))

PROMPT_TEMPLATE = """
You are an expert event planner. Create a concise, actionable plan for a {event_type}.
Include:
- A short timeline (pre-event, event day, post-event)
- Suggested vendors (catering, decor, entertainment, etc.)
- Budget breakdown based on a total of ${budget_usd}
- Personalized ideas to make the event memorable.
Provide the plan in markdown format.
"""


@app.after_request
def apply_security_headers(response: Response) -> Response:
    """Apply standard defense-in-depth security headers."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


def build_prompt(data: Dict[str, Any]) -> str:
    """Construct a clean prompt from validated user inputs.

    Args:
        data: User payload with event_type, event_date, and budget_usd.

    Returns:
        Structured prompt string.
    """
    event_type = str(data.get("event_type", "event"))[:100]
    try:
        budget = max(0.0, float(data.get("budget_usd", 0)))
    except (ValueError, TypeError):
        budget = 0.0

    date = str(data.get("event_date", ""))[:50]
    prompt = PROMPT_TEMPLATE.format(event_type=event_type, budget_usd=budget)
    if date:
        prompt = f"Date: {date}\n" + prompt
    return prompt.strip()


def run_gemma_safely(prompt: str) -> str:
    """Execute the Gemma binary with safe list-based arguments (shell=False).

    Args:
        prompt: The prepared text prompt.

    Returns:
        Generated model output string.
    """
    # Safe argument execution without shell=True prevents command injection
    cmd = [
        GEMMA_EXEC,
        "--model",
        str(MODEL_DIR),
        "--prompt",
        prompt,
    ]

    try:
        result = subprocess.run(
            cmd,
            shell=False,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        # Fallback response if local gemma executable is not installed
        return (
            f"### Plan for Event\n\n"
            f"- **Timeline:** Detailed preparation and milestone schedule.\n"
            f"- **Budget Allocation:** Optimized breakdown.\n"
            f"- **Recommendation:** Local model execution note: {exc}"
        )
    except subprocess.TimeoutExpired:
        return "Error: Generation timed out."


@app.route("/generate", methods=["POST"])
def generate() -> Union[Response, Tuple[Response, int]]:
    """Handle POST request to generate event plan using Gemma."""
    if not request.is_json:
        return jsonify({"error": "JSON payload required"}), 400

    payload = request.get_json(silent=True) or {}
    prompt = build_prompt(payload)
    plan_text = run_gemma_safely(prompt)
    return jsonify({"plan": plan_text})


if __name__ == "__main__":
    is_debug = os.getenv("FLASK_DEBUG", "0") == "1"
    port = int(os.getenv("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=is_debug)
