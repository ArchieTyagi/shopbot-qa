# test_database_and_logs.py
# Testers often check the DATABASE and LOGS directly to find the root cause of a bug.

from pathlib import Path

import requests

from app.database import get_connection

LOG_FILE = Path(__file__).parent.parent / "logs" / "app.log"


def test_order_is_saved_in_database(base_url, token):
    """The API said 'placed'. Is it REALLY in the database?"""
    res = requests.post(
        base_url + "/orders",
        json={"product_id": 1, "quantity": 3},
        headers={"Authorization": f"Bearer {token}"},
    )
    order_id = res.json()["order_id"]

    # Look inside the database with SQL
    conn = get_connection()
    row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    stock = conn.execute("SELECT stock FROM products WHERE id = 1").fetchone()["stock"]
    conn.close()

    assert row is not None
    assert row["quantity"] == 3
    assert stock == 10 - 3


def test_no_product_has_negative_stock():
    """A data check: stock should never go below zero."""
    conn = get_connection()
    bad_rows = conn.execute("SELECT * FROM products WHERE stock < 0").fetchall()
    conn.close()
    assert len(bad_rows) == 0


def test_failed_order_is_written_in_logs(base_url, token):
    """When an order fails, the log must explain WHY. This is how you find root causes."""
    requests.post(
        base_url + "/orders",
        json={"product_id": 3, "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    logs = LOG_FILE.read_text()
    assert "ERROR" in logs
    assert "not enough stock for product 3" in logs
