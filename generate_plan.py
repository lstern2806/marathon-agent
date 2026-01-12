import json
from load_data import load_strava_activities
from summarize_runner import summarize_runs
from prompt_builder import build_prompt
from mock_llm import call_llm

# Load data
df = load_strava_activities("data/activities.csv")
summary = summarize_runs(df)

with open("runner_profile.json") as f:
    runner = json.load(f)

prompt = build_prompt(runner, summary)
response = call_llm(prompt)

plan = json.loads(response)

print("Your AI-generated plan:")
for day, workout in plan.items():
    print(f"{day}: {workout}")

