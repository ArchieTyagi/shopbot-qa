# ShopBot QA

A small online shop with an AI chatbot (Google Gemini), and a full **automated test suite** for it.

This project shows the complete flow of a test automation engineer:
web UI testing, REST API testing, chatbot testing, database checks, log checks, and CI/CD.

## What is inside

```
shopbot-qa/
├── app/                         <- the app we are testing
│   ├── main.py                  <- backend: REST API (login, products, orders, chat)
│   ├── chatbot.py               <- chatbot: guardrails, then Gemini AI (or simple rules)
│   ├── llm.py                   <- talks to the Gemini API
│   ├── database.py              <- SQLite database with sample products
│   └── static/index.html        <- frontend: the web page
├── tests/                       <- the tests (this is the real work)
│   ├── conftest.py              <- setup: starts the server, resets the database
│   ├── test_api.py              <- REST API tests (10 tests)
│   ├── test_chatbot.py          <- chatbot tests that pass in AI and rules mode (15 tests)
│   ├── test_ai_quality.py       <- real AI tests: hallucination, consistency, LLM-as-judge (9 tests)
│   ├── llm_judge.py             <- a second AI that grades the chatbot's answers
│   ├── test_database_and_logs.py<- SQL and log checks (3 tests)
│   └── test_ui_selenium.py      <- browser tests with Selenium (4 tests)
├── postman_collection.json      <- same API tests, for Postman
└── .github/workflows/tests.yml  <- CI: runs all tests on every push
```

## How to run it

You need Python 3.10+ and Google Chrome installed.

```bash
# 1. Install packages
pip install -r requirements.txt

# 2. Start the shop (open http://127.0.0.1:8000 in your browser)
uvicorn app.main:app --reload
#    Login with:  archi / test123

# 3. Stop the server (Ctrl+C), then run all tests.
#    pytest starts its own copy of the server, so the port must be free.
pytest
```

Run just one group of tests:

```bash
pytest tests/test_api.py
pytest tests/test_chatbot.py
pytest tests/test_ui_selenium.py      # you will SEE Chrome open and click by itself
```

## Turning on the real AI (Gemini)

1. Get a free API key at https://aistudio.google.com/apikey
2. Set it in your terminal before starting the app or running tests:
   ```bash
   export GEMINI_API_KEY="your-key-here"
   ```
3. Start the app. The chat box now says **(powered by Gemini AI)**.

Without a key, the chatbot uses simple rules and the AI-only tests are skipped, so nothing breaks.

How a chat message flows:

```
user message -> guardrails (block tricks and harmful requests)
             -> Gemini, given the REAL products and prices from the database
             -> reply
```

The model can be changed with `GEMINI_MODEL` (default: `gemini-2.5-flash`).

## The flow (how the pieces connect)

```
   You (tester)
       │ write tests
       ▼
  ┌─────────────┐   Selenium clicks   ┌──────────────┐   REST API   ┌──────────────┐
  │   pytest    │ ──────────────────▶ │  Web page    │ ───────────▶ │   Backend    │
  │ (the robot) │ ───── requests ───────────────────────────────▶  │  (FastAPI)   │
  └─────────────┘                     └──────────────┘              └──────┬───────┘
       │ reads SQL + logs directly                                        │
       └─────────────────────────────▶  shop.db  +  logs/app.log  ◀───────┘
```

1. **UI tests** use Selenium to open Chrome and act like a real user.
2. **API tests** skip the browser and talk to the backend directly (like Postman).
3. **Chatbot tests** check meaning, facts, and safety, never the exact sentence.
4. **Database and log tests** look behind the scenes to confirm what really happened.
5. **GitHub Actions** runs all of it automatically on every push.

## What each test file teaches

| File | Testing idea |
|------|--------------|
| `test_api.py` | Status codes (200, 201, 400, 401, 404), checking JSON data, unit vs integration test |
| `test_chatbot.py` | Testing answers that change every time: facts, safety, prompt injection, speed |
| `test_ai_quality.py` | Real LLM testing: no made-up products, same facts for different wordings, LLM-as-judge |
| `test_database_and_logs.py` | Using SQL and logs to find the root cause of a bug |
| `test_ui_selenium.py` | Locators (`By.ID`, `By.CLASS_NAME`), waits, clicking and typing |

## Try this: find a bug like a real tester

1. Open `app/main.py` and find this line:
   ```python
   "UPDATE products SET stock = stock - ? WHERE id = ?",
   ```
2. Change `-` to `+` (now buying something ADDS stock, a bug).
3. Run `pytest`. Which tests fail? Read the error message.
4. Open `logs/app.log` and see what the app recorded.
5. Fix it back and run `pytest` again. Everything passes. That is a **regression test** in action.

## Using Postman

Open Postman, click **Import**, and choose `postman_collection.json`.
Start the server, then click **Send** on each request. The **Test Results** tab shows pass or fail.

## Tech used

Python, pytest, Selenium, requests, FastAPI, SQLite, Google Gemini API, Postman, Git, GitHub Actions
