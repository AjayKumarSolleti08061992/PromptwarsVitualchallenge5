# server.py – Simple Flask backend that wraps the Gemma model (gemma.cpp)
#
# This server receives a JSON payload with event details, forwards it to the
# Gemma executable, and returns the generated marketing‑style plan.
#
# Prerequisites:
#   1. Install Python 3.10+ and pip.
#   2. Install Flask: pip install flask
#   3. Build gemma.cpp (see https://github.com/google/gemma.cpp) and ensure the
#      executable ``gemma`` is in your PATH or provide the absolute path.
#   4. Download a Gemma model checkpoint (e.g., 2B, 7B) and place it in a
#      directory accessible to the server.
#
# The server runs on http://127.0.0.1:5000/generate and expects a POST request
# with a JSON body containing the fields ``event_type``, ``event_date`` and
# ``budget_usd``.
#
# Example request payload:
# {
#   "event_type": "wedding",
#   "event_date": "2024-06-15",
#   "budget_usd": 20000
# }
#
# The response format matches what ``script.js`` expects:
# { "plan": "...generated markdown..." }

import json
import subprocess
import shlex
from pathlib import Path
from typing import Dict

from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Configuration – adjust these paths according to your setup
# ---------------------------------------------------------------------------
# Path to the compiled Gemma executable. If ``gemma`` is on your PATH you can
# simply use "gemma". Otherwise provide an absolute path, e.g.
# GEMMA_EXEC = "C:/tools/gemma.exe"
GEMMA_EXEC = "gemma"
# Directory that contains the downloaded Gemma model checkpoint.
# The checkpoint directory should contain files such as "model.ggml"
MODEL_DIR = Path("models/gemma-2b")

# Prompt template – feel free to customise the wording to match your style.
PROMPT_TEMPLATE = """
You are an expert event planner. Create a concise, actionable plan for a {event_type}.
Include:
- A short timeline (pre‑event, event day, post‑event)
- Suggested vendors (catering, decor, entertainment, etc.)
- Budget breakdown based on a total of ${budget_usd}
- Personalized ideas to make the event memorable.
Provide the plan in markdown format.
"""


def build_prompt(data: Dict) -> str:
    """Construct the prompt for Gemma using the user‑provided data.

    Parameters
    ----------
    data: dict
        Keys ``event_type``, ``event_date`` and ``budget_usd``.
    """
    event_type = data.get("event_type", "event")
    budget = data.get("budget_usd", 0)
    # The date is optional for the model; we embed it for context.
    date = data.get("event_date", "")
    prompt = PROMPT_TEMPLATE.format(event_type=event_type, budget_usd=budget)
    if date:
        prompt = f"Date: {date}\n" + prompt
    return prompt.strip()


def run_gemma(prompt: str) -> str:
    """Execute the Gemma binary with the given prompt.

    The function streams the model's stdout and returns the complete output.
    It assumes the Gemma binary accepts ``--prompt`` and ``--model`` arguments –
    adjust if your build uses a different CLI.
    """
    # Build the command line safely – use shlex.quote for Windows compatibility.
    cmd = f"{shlex.quote(GEMMA_EXEC)} --model {shlex.quote(str(MODEL_DIR))} --prompt {shlex.quote(prompt)}"
    try:
        # ``capture_output=True`` returns stdout as bytes.
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as exc:
        # Log the error and return a friendly message.
        print(f"Gemma execution failed: {exc}")
        return "Error: failed to generate plan."
    except subprocess.TimeoutExpired:
        return "Error: generation timed out."


@app.route("/generate", methods=["POST"])
def generate():
    """Flask endpoint that forwards the request to Gemma and returns the plan.
    """
    if not request.is_json:
        return jsonify({"error": "JSON payload required"}), 400
    payload = request.get_json()
    prompt = build_prompt(payload)
    plan_text = run_gemma(prompt)
    return jsonify({"plan": plan_text})


if __name__ == "__main__":
    # Run the development server; for production use a WSGI server like gunicorn.
    app.run(host="127.0.0.1", port=5000, debug=True)
