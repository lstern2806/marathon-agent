### Marathon Agent
Marathon Agent is a personalized AI-powered running coach built to support my personal half-marathon training by combining my real Strava 
running data, a structured training plan, and a conversational AI interface. I'm building this while training for my half marathon 
because I wanted more than a static plan — I wanted an agent that could understand my mileage, pace, fatigue, and schedule and give me 
adaptive, data-driven guidance. The system ingests my running history, tracks weekly volume and pacing trends, and uses a large language 
model to answer questions, generate weekly plans, and help me make smarter training decisions in real time through both a terminal and 
web-based interface.

The project is implemented in Python and uses the OpenAI API to power a large-language-model–based coaching agent. It integrates Strava 
activity data, structured JSON training plans, and a Flask-based web interface to create a fully personalized, data-driven training 
system.

## Tech Stack:
Python and Pandas for data processing, OpenAI’s API for the AI coaching agent, Flask for the backend API, and a lightweight 
HTML/JavaScript frontend for the web interface, with training plans and user data stored in JSON.

## How to run

1. Clone the repository

2. Install dependencies: 
    pip install -r requirements.txt

3. Add a Strava activity export to data/activities.csv

4. Generate the runner history file:
    python3 build_history.py

5. Start the web app:
    python3 web_app.py

6. Then open http://localhost:5000 in your browser.

### This project is actively under development as my training progresses and new features (such as improved analytics and calendar-based planning) are being added.
