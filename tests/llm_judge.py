# llm_judge.py
# "LLM-as-judge": a SECOND AI grades the chatbot's answer, like a teacher checking homework.
# Used when an answer can be correct in many different wordings.

import json

from app import llm

JUDGE_PROMPT = """You are a strict QA reviewer grading a shop chatbot's answer.
Give a score from 1 to 5:
5 = fully correct, follows the facts and rules, helpful
3 = partly correct or missing something
1 = wrong, made-up facts, or broke the rules
Reply ONLY with JSON like: {"score": 4, "reason": "short reason"}"""


def judge(question: str, answer: str, facts: str) -> dict:
    message = f"Facts the answer must follow:\n{facts}\n\nQuestion: {question}\nAnswer: {answer}"
    return json.loads(llm.ask_gemini(JUDGE_PROMPT, message, json_output=True))
