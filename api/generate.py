import json, subprocess, shlex, os

def build_prompt(data):
    """Create the Gemma prompt from the incoming request JSON."""
    event_type = data.get('event_type', 'event')
    budget = data.get('budget_usd', 0)
    date = data.get('event_date', '')
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

def handler(request):
    """Vercel serverless function entry point.
    Expects JSON body with keys: event_type, event_date, budget_usd.
    Returns JSON with a "plan" field.
    """
    try:
        data = request.get_json()
        prompt = build_prompt(data)
        # Path to Gemma executable and model directory – can be overridden via env vars in Vercel.
        GEMMA_EXEC = os.getenv('GEMMA_EXEC', 'gemma')
        MODEL_DIR = os.getenv('MODEL_DIR', 'models/gemma-2b')
        cmd = f"{shlex.quote(GEMMA_EXEC)} --model {shlex.quote(MODEL_DIR)} --prompt {shlex.quote(prompt)}"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        plan = result.stdout.strip()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"plan": plan}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
