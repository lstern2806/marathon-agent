import json
from datetime import datetime

from load_data import load_strava_activities
from summarize_runner import summarize_runs
from prompt_builder import build_prompt
from llm_openai import call_llm
from plan_tools import load_plan, get_week, pretty_week, workout_on
from datetime import date, timedelta
from plan_tools import week_for_date, next_week
from coach_prompt import build_coach_chat_prompt
from datetime import date

MEMORY_PATH = "memory.json"
DATA_PATH = "data/activities.csv"

def load_memory():
    with open(MEMORY_PATH, "r") as f:
        return json.load(f)

def save_memory(mem):
    with open(MEMORY_PATH, "w") as f:
        json.dump(mem, f, indent=2)

def get_training_summary():
    df = load_strava_activities(DATA_PATH)
    return summarize_runs(df)

def generate_plan(mem):
    runner = mem["runner_profile"]
    summary = get_training_summary()

    # include notes in the prompt (injuries, soreness, constraints)
    notes = mem.get("notes", [])
    runner_context = dict(runner)
    runner_context["notes"] = notes

    prompt = build_prompt(runner_context, summary)
    response = call_llm(prompt)  # swap this later with real LLM API
    plan = json.loads(response)

    mem["last_plan"] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": summary,
        "plan": plan
    }
    save_memory(mem)
    return plan, summary

def show_last_plan(mem):
    lp = mem.get("last_plan")
    if not lp:
        print("No plan generated yet. Type: plan")
        return
    print(f"\nLast plan (generated {lp['generated_at']}):")
    for day, workout in lp["plan"].items():
        print(f"  {day}: {workout}")

def add_note(mem, note_text):
    mem.setdefault("notes", []).append({
        "time": datetime.now().isoformat(timespec="seconds"),
        "text": note_text
    })
    save_memory(mem)
    print("Saved note ✅")

def show_status(mem):
    summary = get_training_summary()
    print("\nTraining status (last 56 days):")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    notes = mem.get("notes", [])
    if notes:
        print("\nNotes:")
        for n in notes[-5:]:
            print(f"  - {n['time']}: {n['text']}")
def load_runner_history(path="runner_history.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def help_text():
    print("""
Commands:
  plan                Generate a new 7-day plan (uses Strava + profile + notes)
  last                Show last generated plan
  status              Show training summary + recent notes
  note <text>         Save a note (e.g., soreness, schedule changes)
  profile             Show runner profile
  plan week <n>         Show a specific week from your reference plan (e.g., plan week 1)
  plan today            Show today's scheduled workout from reference plan
  plan tomorrow         Show tomorrow's scheduled workout from reference plan
  chat <question>       Ask coaching questions about your reference plan + your training
  exit                Quit
""".strip())

def main():
    mem = load_memory()
    plan_ref = load_plan()
    print("🏃 Marathon Agent (Terminal) — type 'help' to see commands.\n")

    while True:
        try:
            cmd = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye!")
            break

        if not cmd:
            continue

        if cmd == "help":
            help_text()
        elif cmd == "exit":
            print("bye!")
            break
        elif cmd == "profile":
            print(json.dumps(mem["runner_profile"], indent=2))
        elif cmd == "status":
            show_status(mem)
        elif cmd == "plan":
            plan, summary = generate_plan(mem)
            print("\n✅ Generated plan:")
            for day, workout in plan.items():
                print(f"  {day}: {workout}")
        elif cmd == "last":
            show_last_plan(mem)
        elif cmd == "note":
            note_text = input("note> ").strip()
            if note_text:
                add_note(mem, note_text)
            else: 
                print("No note saved.")
        elif cmd.startswith("note "):
            add_note(mem, cmd[len("note "):].strip())
        elif cmd.startswith("plan week "):
            wk = cmd[len("plan week "):].strip()
            w = get_week(plan_ref, f"Week {wk}" if wk.isdigit() else wk)
            if not w:
                print("Week not found. Try: plan week 1")
            else:
                print(pretty_week(w))

        elif cmd == "plan today":
            wk, dow, workout = workout_on(plan_ref, date.today())
            print(f"{wk or 'Unknown week'} — {dow}: {workout or 'No workout found'}")

        elif cmd == "plan tomorrow":
            d = date.today() + timedelta(days=1)
            wk, dow, workout = workout_on(plan_ref, d)
            print(f"{d.isoformat()} ({wk or 'Unknown week'}) — {dow}: {workout or 'No workout found'}")
        
        elif cmd.startswith("chat "):
            question = cmd[len("chat "):].strip()
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
            print("\ncoach> " + answer.strip())

        else:
            print("Unknown command. Type 'help'.")

if __name__ == "__main__":
    main()

