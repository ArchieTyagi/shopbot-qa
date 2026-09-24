# llm.py
# Talks to Google Gemini, a real AI model (LLM).
#
# You need a free API key from https://aistudio.google.com/apikey
# Put it in an environment variable called GEMINI_API_KEY.
# If there is no key, the app uses the simple rule-based bot instead.

import os
import time

import requests

GEMINI_URL = os.getenv(
    "GEMINI_URL", "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


def is_enabled() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))


def ask_gemini(system_prompt: str, user_message: str, json_output: bool = False) -> str:
    """Send one message to Gemini and return its text answer."""
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    body = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {"temperature": 0.7},
    }
    if json_output:
        body["generationConfig"]["responseMimeType"] = "application/json"

    # Free keys have a limit on requests per minute.
    # If Gemini says "too many requests" (429), wait and try again.
    for attempt in range(5):
        res = requests.post(
            GEMINI_URL.format(model=model),
            headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
            json=body,
            timeout=30,
        )
        if res.status_code in (429, 503):
            time.sleep(5 * (attempt + 1))
            continue
        res.raise_for_status()
        return res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    raise RuntimeError("Gemini is busy (rate limit). Try again in a minute.")
