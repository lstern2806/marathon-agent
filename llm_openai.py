import os
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from env automatically :contentReference[oaicite:3]{index=3}

def call_llm(prompt: str) -> str:
    """
    Returns a JSON string that our agent will json.loads(...)
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to your environment variables.")

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt,
    )
    return response.output_text

