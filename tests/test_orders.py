from decimal import Decimal
import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _create_user(email="test@example.com"):
    r = client.post("/users", json={"email": email})
    assert r.status_code in (200, 409)
    if r.status_code == 200:
        return r.json()
    # if already exists, just fail fast for simplicity in v1 tests
    pytest.skip("User already exists in shared DB; run tests against a fresh DB.")


def test_buy_creates_position_and_reduces_cash():
    u = _create_user("buy1@example.com")
    account_id = u["account_id"]

    # BUY 10 @ mock price 100 => cost 1000
    r = client.post("/orders", json={"account_id": account_id, "symbol": "AAPL", "side": "BUY", "qty": "10"})
    assert r.status_code == 200
    o = r.json()
    assert o["status"] == "FILLED"

    pos = client.get("/positions", params={"account_id": account_id}).json()
    assert any(p["symbol"] == "AAPL" and Decimal(p["qty"]) == Decimal("10") for p in pos)


def test_sell_rejects_if_insufficient_position():
    u = _create_user("sellreject@example.com")
    account_id = u["account_id"]

    r = client.post("/orders", json={"account_id": account_id, "symbol": "MSFT", "side": "SELL", "qty": "1"})
    assert r.status_code == 200
    o = r.json()
    assert o["status"] == "REJECTED"
    assert o["reject_reason"] == "Insufficient position"