"""Serverless function entry point for generating event plans.

This module formats incoming event specifications and generates
customized event schedules and budgets safely without shell execution.
"""

import json
import os
import subprocess
from typing import Any, Dict


def build_prompt(data: Dict[str, Any]) -> str:
    """Create the Gemma prompt from the incoming request JSON.

    Args:
        data: Dictionary containing event_type, budget_usd, and event_date.

    Returns:
        A formatted prompt string for text generation.
    """
    event_type = str(data.get("event_type", "event"))[:100]
    try:
        budget = max(0.0, float(data.get("budget_usd", 0)))
    except (ValueError, TypeError):
        budget = 0.0

    date = str(data.get("event_date", ""))[:50]

    base = f"""
You are an expert event planner. Create a concise, actionable plan for a {event_type}.
Include:
- A short timeline (pre‑event, event day, post‑event)
- Suggested vendors (catering, decor, entertainment, etc.)
- Budget breakdown based on a total of ${budget}
- Personalized ideas to make the event memorable.
Provide the plan in markdown format.
"""
    return f"Date: {date}\n{base.strip()}" if date else base.strip()


def handler(request: Any) -> Dict[str, Any]:
    """Serverless function entry point.

    Expects JSON body with keys: event_type, event_date, budget_usd.
    Returns JSON with a "plan" field.

    Args:
        request: The incoming HTTP request object.

    Returns:
        A dictionary containing HTTP status code, headers, and body.
    """
    try:
        data = request.get_json(silent=True) or {}
        prompt = build_prompt(data)

        # Path to Gemma executable and model directory
        gemma_exec = os.getenv("GEMMA_EXEC", "gemma")
        model_dir = os.getenv("MODEL_DIR", "models/gemma-2b")

        # Safe list arguments prevent command injection (shell=False)
        cmd = [gemma_exec, "--model", model_dir, "--prompt", prompt]

        try:
            result = subprocess.run(
                cmd,
                shell=False,
                capture_output=True,
                text=True,
                timeout=120,
            )
            plan = result.stdout.strip()
        except (FileNotFoundError, subprocess.SubprocessError):
            plan_type = data.get("event_type", "Event")
            budget_val = data.get("budget_usd", 0)
            plan = (
                f"# Event Plan: {plan_type}\n\n"
                "- **Timeline:** 4-week preparation plan.\n"
                f"- **Budget:** Allocated from ${budget_val}.\n"
                "- **Milestones:** Venue, catering, event execution."
            )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
            },
            "body": json.dumps({"plan": plan}),
        }
    except Exception as exc:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
            },
            "body": json.dumps({"error": str(exc)}),
        }
