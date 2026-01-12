import json

def build_coach_chat_prompt(question, runner_profile, summary, notes, current_week, next_week, history):
    ctx = {
        "runner_profile": runner_profile,
        "training_summary": summary,
        "notes": notes[-10:],  # last 10 notes
        "current_week": current_week,
        "next_week": next_week,
        "runner_history": history
    }

    return f"""
You are a helpful, safety-minded running coach. Answer the user's question using the plan context.

Context (JSON):
{json.dumps(ctx, indent=2)}

User question:
{question}

Guidelines:
- Keep advice aligned with the provided plan unless the user asks to modify it.
- If suggesting changes, give a clear, conservative adjustment.
- Be concise and specific.
""".strip()

