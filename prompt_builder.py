import json

def build_prompt(runner_profile, summary):
    return f"""
You are an expert running coach.

Runner profile:
{json.dumps(runner_profile, indent=2)}

Recent training summary:
{json.dumps(summary, indent=2)}

Task:
Create a training plan for the next 7 days.


Hard rules:
- Output MUST be valid JSON and NOTHING ELSE.
- JSON keys must be exactly: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
- Each value must be a single string describing the workout.
- Respect availability and long run day.
- Keep mileage progression safe based on recent weekly mileage.

Return JSON only.
""".strip()
