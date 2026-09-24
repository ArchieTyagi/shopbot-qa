# test_api.py
# REST API tests. Same idea as clicking "Send" in Postman, but in code.
# Every test follows 3 steps:  ARRANGE (prepare)  ->  ACT (send request)  ->  ASSERT (check result)

import requests


# ---------- Login ----------
def test_login_with_correct_password(base_url):
    res = requests.post(base_url + "/login", json={"username": "archi", "password": "test123"})
    assert res.status_code == 200
    assert "token" in res.json()


def test_login_with_wrong_password(base_url):
    res = requests.post(base_url + "/login", json={"username": "archi", "password": "wrong"})
    assert res.status_code == 401


# ---------- Products ----------
def test_get_all_products(base_url):
    res = requests.get(base_url + "/products")
    assert res.status_code == 200
    products = res.json()
    assert len(products) == 3
    # every product must have these fields
    for p in products:
        assert set(p.keys()) == {"id", "name", "price", "stock"}


def test_get_one_product(base_url):
    res = requests.get(base_url + "/products/1")
    assert res.status_code == 200
    assert res.json()["name"] == "Headphones"
    assert res.json()["price"] == 1999


def test_product_not_found(base_url):
    res = requests.get(base_url + "/products/999")
    assert res.status_code == 404


# ---------- Orders ----------
def test_place_order(base_url, token):
    res = requests.post(
        base_url + "/orders",
        json={"product_id": 1, "quantity": 2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    assert res.json()["status"] == "placed"


def test_order_without_login_is_blocked(base_url):
    res = requests.post(base_url + "/orders", json={"product_id": 1, "quantity": 1})
    assert res.status_code == 401


def test_order_out_of_stock_product(base_url, token):
    # Mouse (id 3) has 0 stock
    res = requests.post(
        base_url + "/orders",
        json={"product_id": 3, "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert res.json()["detail"] == "Not enough stock"


def test_order_with_zero_quantity(base_url, token):
    res = requests.post(
        base_url + "/orders",
        json={"product_id": 1, "quantity": 0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400


# ---------- Integration test: many parts working together ----------
def test_full_order_flow(base_url, token):
    """Login -> place order -> check order -> check stock went down."""
    headers = {"Authorization": f"Bearer {token}"}

    stock_before = requests.get(base_url + "/products/2").json()["stock"]

    order = requests.post(
        base_url + "/orders", json={"product_id": 2, "quantity": 1}, headers=headers
    ).json()

    saved = requests.get(base_url + f"/orders/{order['order_id']}").json()
    assert saved["product_id"] == 2
    assert saved["status"] == "placed"

    stock_after = requests.get(base_url + "/products/2").json()["stock"]
    assert stock_after == stock_before - 1
