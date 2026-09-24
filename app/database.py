# database.py
# Creates a small SQLite database (a single file: shop.db) and fills it with sample data.

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "shop.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # lets us read rows like dictionaries
    return conn


def setup_database():
    """Delete old data and create fresh tables with sample products."""
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS orders;

        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            stock INTEGER NOT NULL
        );

        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL
        );
        """
    )
    cur.executemany(
        "INSERT INTO products (id, name, price, stock) VALUES (?, ?, ?, ?)",
        [
            (1, "Headphones", 1999, 10),
            (2, "Keyboard", 1499, 5),
            (3, "Mouse", 599, 0),  # out of stock on purpose
        ],
    )
    conn.commit()
    conn.close()
