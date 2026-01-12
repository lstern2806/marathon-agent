from flask import Flask, request, jsonify, send_from_directory
from datetime import date, timedelta
import json

# --- import your existing stuff ---
from plan_tools import load_plan, workout_on, week_for_date, next_week
from coach_prompt import build_coach_chat_prompt
from llm_openai import call_llm

# If these exist in your project already, import them:
# - load_memory()
# - save_memory() (optional)
# - get_training_summary() (your Strava summary)
from agent import load_memory, get_training_summary  # adjust if your names differ

def load_runner_history(path="runner_history.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

app = Flask(__name__, static_folder="web", static_url_path="")

mem = load_memory()
plan_ref = load_plan()

@app.get("/")
def index():
    return send_from_directory("web", "index.html")

@app.get("/api/status")
def api_status():
    summary = get_training_summary()
    history = load_runner_history()
    return jsonify({
        "runner_profile": mem.get("runner_profile"),
        "training_summary": summary,
        "runner_history": history,
        "notes": mem.get("notes", [])[-10:]
    })

@app.get("/api/plan/today")
def api_plan_today():
    wk, dow, workout = workout_on(plan_ref, date.today())
    return jsonify({"date": date.today().isoformat(), "week": wk, "day": dow, "workout": workout})

@app.get("/api/plan/tomorrow")
def api_plan_tomorrow():
    d = date.today() + timedelta(days=1)
    wk, dow, workout = workout_on(plan_ref, d)
    return jsonify({"date": d.isoformat(), "week": wk, "day": dow, "workout": workout})

@app.post("/api/note")
def api_note():
    data = request.get_json(force=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Missing note text"}), 400
    mem.setdefault("notes", []).append({"ts": date.today().isoformat(), "text": text})
    # If you have a save_memory() function, call it here:
    # save_memory(mem)
    return jsonify({"ok": True})

@app.post("/api/chat")
def api_chat():
    data = request.get_json(force=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "Missing question"}), 400

    summary = get_training_summary()
    notes = mem.get("notes", [])
    history = load_runner_history()

    cw = week_for_date(plan_ref, date.today())
    nw = next_week(plan_ref, date.today())

    prompt = build_coach_chat_prompt(
        question=question,
        runner_profile=mem["runner_profile"],
        summary=summary,
        notes=notes,
        current_week=cw,
        next_week=nw,
        history=history
    )

    answer = call_llm(prompt)
    return jsonify({"answer": answer.strip()})

@app.get("/api/plan/week")
def api_plan_week():
    # Optional query param: ?start=YYYY-MM-DD
    start_str = request.args.get("start")
    if start_str:
        start = date.fromisoformat(start_str)
    else:
        # default: Monday of current week
        today = date.today()
        start = today - timedelta(days=today.weekday())

    days = []
    for i in range(7):
        d = start + timedelta(days=i)
        wk, dow, workout = workout_on(plan_ref, d)
        days.append({
            "date": d.isoformat(),
            "weekday": dow,
            "week_label": wk,
            "workout": workout or "OFF"
        })

    return jsonify({
        "start": start.isoformat(),
        "end": (start + timedelta(days=6)).isoformat(),
        "days": days
    })


if __name__ == "__main__":
    # http://127.0.0.1:5000
    app.run(debug=True)

