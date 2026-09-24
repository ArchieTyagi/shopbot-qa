# main.py
# The backend of our shop. It gives us REST API endpoints:
#
#   POST /login           -> get a token
#   GET  /products        -> list all products
#   GET  /products/{id}   -> one product
#   POST /orders          -> place an order (needs token)
#   GET  /orders/{id}     -> check an order
#   POST /chat            -> talk to the chatbot
#   GET  /                -> the web page (frontend)
#
# Run it with:  uvicorn app.main:app --reload

import logging
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.chatbot import get_reply
from app.database import get_connection, setup_database

# ---------- Logs: the app's diary ----------
LOG_FILE = Path(__file__).parent.parent / "logs" / "app.log"
LOG_FILE.parent.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("shopbot")

app = FastAPI(title="ShopBot")
setup_database()

# One test user and one fixed token (a real app would use a proper login system)
USERS = {"archi": "test123"}
VALID_TOKEN = "token-archi-123"


# ---------- Request shapes ----------
class LoginRequest(BaseModel):
    username: str
    password: str


class OrderRequest(BaseModel):
    product_id: int
    quantity: int


class ChatRequest(BaseModel):
    message: str


# ---------- Endpoints ----------
@app.get("/")
def home():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.post("/login")
def login(body: LoginRequest):
    if USERS.get(body.username) != body.password:
        log.warning(f"Failed login for user '{body.username}'")
        raise HTTPException(status_code=401, detail="Wrong username or password")
    log.info(f"User '{body.username}' logged in")
    return {"token": VALID_TOKEN}


@app.get("/products")
def list_products():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/products/{product_id}")
def get_product(product_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    if row is None:
        log.error(f"Product {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)


@app.post("/orders", status_code=201)
def create_order(body: OrderRequest, authorization: str = Header(default="")):
    if authorization != f"Bearer {VALID_TOKEN}":
        log.warning("Order attempt without a valid token")
        raise HTTPException(status_code=401, detail="Please log in first")

    if body.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    conn = get_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (body.product_id,)).fetchone()
    if product is None:
        conn.close()
        log.error(f"Order failed: product {body.product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    if product["stock"] < body.quantity:
        conn.close()
        log.error(
            f"Order failed: not enough stock for product {body.product_id} "
            f"(wanted {body.quantity}, have {product['stock']})"
        )
        raise HTTPException(status_code=400, detail="Not enough stock")

    cur = conn.execute(
        "INSERT INTO orders (product_id, quantity, status) VALUES (?, ?, 'placed')",
        (body.product_id, body.quantity),
    )
    conn.execute(
        "UPDATE products SET stock = stock - ? WHERE id = ?",
        (body.quantity, body.product_id),
    )
    conn.commit()
    order_id = cur.lastrowid
    conn.close()
    log.info(f"Order {order_id} placed: product {body.product_id} x {body.quantity}")
    return {"order_id": order_id, "status": "placed"}


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return dict(row)


@app.post("/chat")
def chat(body: ChatRequest):
    reply = get_reply(body.message)
    log.info(f"Chat | user: {body.message!r} | bot: {reply!r}")
    return {"reply": reply}
