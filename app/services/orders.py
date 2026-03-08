from fastapi import HTTPException
from app.models import Order, Account
from app.config import settings


def create_order(db, order_in):
    # find account for this user
    account = db.query(Account).filter(Account.user_id == order_in.user_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    order = Order(
        account_id=account.id,
        symbol=order_in.symbol,
        side=order_in.side,
        quantity=order_in.quantity
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order