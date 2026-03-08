from __future__ import annotations

from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Account, Position, Order
from app.config import settings


def _normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def place_market_order(db: Session, *, account_id: int, symbol: str, side: str, qty: Decimal) -> Order:
    """
    Executes a simulated MARKET order at a fixed mock price.
    Critical: transaction-safe; caller should commit/rollback.
    """
    symbol_n = _normalize_symbol(symbol)
    price = settings.mock_fill_price

    acct = db.execute(select(Account).where(Account.id == account_id).with_for_update()).scalar_one_or_none()
    if not acct:
        o = Order(
            account_id=account_id,
            symbol=symbol_n,
            side=side,
            qty=qty,
            status="REJECTED",
            filled_price=None,
            reject_reason="Account not found",
        )
        db.add(o)
        db.flush()
        return o

    # lock position row if exists
    pos = db.execute(
        select(Position)
        .where(Position.account_id == account_id, Position.symbol == symbol_n)
        .with_for_update()
    ).scalar_one_or_none()

    notional = (qty * price).quantize(Decimal("0.01"))

    if side == "BUY":
        if Decimal(acct.cash_balance) < notional:
            o = Order(
                account_id=account_id,
                symbol=symbol_n,
                side=side,
                qty=qty,
                status="REJECTED",
                filled_price=None,
                reject_reason="Insufficient funds",
            )
            db.add(o)
            db.flush()
            return o

        # update cash
        acct.cash_balance = (Decimal(acct.cash_balance) - notional).quantize(Decimal("0.01"))

        # upsert position w/ weighted avg cost
        if pos is None:
            pos = Position(account_id=account_id, symbol=symbol_n, qty=qty, avg_cost=price)
            db.add(pos)
        else:
            old_qty = Decimal(pos.qty)
            old_cost = Decimal(pos.avg_cost)
            new_qty = old_qty + qty
            # weighted avg = (old_qty*old_cost + qty*price) / new_qty
            new_avg = (old_qty * old_cost + qty * price) / new_qty
            pos.qty = new_qty
            pos.avg_cost = new_avg

        o = Order(
            account_id=account_id,
            symbol=symbol_n,
            side=side,
            qty=qty,
            status="FILLED",
            filled_price=price,
            reject_reason=None,
        )
        db.add(o)
        db.flush()
        return o

    # SELL
    if pos is None or Decimal(pos.qty) < qty:
        o = Order(
            account_id=account_id,
            symbol=symbol_n,
            side=side,
            qty=qty,
            status="REJECTED",
            filled_price=None,
            reject_reason="Insufficient position",
        )
        db.add(o)
        db.flush()
        return o

    # update position + cash
    pos.qty = Decimal(pos.qty) - qty
    acct.cash_balance = (Decimal(acct.cash_balance) + notional).quantize(Decimal("0.01"))

    # if position becomes zero, delete it (optional)
    if Decimal(pos.qty) == 0:
        db.delete(pos)

    o = Order(
        account_id=account_id,
        symbol=symbol_n,
        side=side,
        qty=qty,
        status="FILLED",
        filled_price=price,
        reject_reason=None,
    )
    db.add(o)
    db.flush()
    return o