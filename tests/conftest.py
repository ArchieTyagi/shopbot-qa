# conftest.py
# pytest runs this file first. It sets up things ("fixtures") that every test can use.

import subprocess
import sys
import time

import pytest
import requests

from app.database import setup_database

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session", autouse=True)
def server():
    """Start the shop server once before all tests, stop it after."""
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Wait until the server answers (max 15 seconds)
    for _ in range(30):
        try:
            requests.get(BASE_URL + "/products", timeout=1)
            break
        except requests.ConnectionError:
            time.sleep(0.5)
    else:
        process.kill()
        pytest.exit("Server did not start")

    yield

    process.terminate()


@pytest.fixture(autouse=True)
def fresh_database():
    """Reset the database before EVERY test, so tests don't affect each other."""
    setup_database()


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def chat_mode():
    """'ai' if the bot uses Gemini, 'rules' if it uses the simple rule-based bot."""
    return requests.get(BASE_URL + "/chat/mode").json()["mode"]


def ask(message):
    """Send a message to the chatbot and return its reply (commas removed, so 1,499 == 1499)."""
    res = requests.post(BASE_URL + "/chat", json={"message": message}, timeout=120)
    assert res.status_code == 200
    return res.json()["reply"].replace(",", "")


@pytest.fixture
def token(base_url):
    """Log in and return a token, for tests that need a logged-in user."""
    res = requests.post(base_url + "/login", json={"username": "archi", "password": "test123"})
    return res.json()["token"]
