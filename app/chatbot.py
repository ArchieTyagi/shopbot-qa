# chatbot.py
# A simple shop assistant chatbot.
#
# In a real company this would call an LLM (like GPT or Claude).
# Here it is rule based so the project runs for free, without any API key.
# The TESTS are written the same way you would test a real LLM:
# we never check the exact sentence, only the important parts.

import random

from app.database import get_connection

# Phrases that try to trick the bot ("prompt injection")
INJECTION_PHRASES = ["ignore your rules", "ignore previous", "system prompt", "you are now"]

# Topics the bot must refuse
BLOCKED_TOPICS = ["hack", "password of", "credit card number"]


def get_reply(message: str) -> str:
    text = message.lower().strip()

    if text == "":
        return "Please type a question about our shop."

    # 1. Safety first: refuse tricks and harmful requests
    if any(p in text for p in INJECTION_PHRASES):
        return "Sorry, I can't do that. I can only help with shop questions."
    if any(t in text for t in BLOCKED_TOPICS):
        return "Sorry, I can't help with that request."

    # 2. Greetings (random wording, just like a real LLM)
    if text in ["hi", "hello", "hey"]:
        return random.choice(
            [
                "Hi! How can I help you with your shopping today?",
                "Hello! Ask me about products, prices or orders.",
                "Hey there! What are you looking for today?",
            ]
        )

    # 3. Policy questions (checked BEFORE products, so "when will keyboard deliver" works)
    if "refund" in text or "return" in text:
        return "You can return any product within 7 days for a full refund."
    if "deliver" in text or "shipping" in text:
        return "Delivery takes 3 to 5 days. Shipping is free above ₹999."

    # 4. Product questions: look up real data in the database
    conn = get_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    for p in products:
        if p["name"].lower() in text:
            if p["stock"] == 0:
                return f"{p['name']} costs ₹{p['price']} but it is out of stock right now."
            return f"{p['name']} costs ₹{p['price']} and we have {p['stock']} in stock."

    # 5. Anything else
    return "I'm not sure about that. I can help with products, prices, orders, refunds and delivery."
