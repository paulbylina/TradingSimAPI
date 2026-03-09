from fastapi import HTTPException
from app.models import Order, Account, Position
from app.config import settings


def create_order(db, order_in):
    # find account for this user
    account = db.query(Account).filter(Account.user_id == order_in.user_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    symbol = order_in.symbol.strip().upper()
    side = order_in.side.strip().upper()

    order = Order(
        account_id=account.id,
        symbol=symbol,
        side=side,
        quantity=order_in.quantity,
        status="filled",
        filled_price=settings.mock_fill_price,
        reject_reason=None,
    )
    
    # Trade Value
    trade_value = order.quantity * order.filled_price

    # Checks if account already has a position open for that symbol
    position = db.query(Position).filter(
    Position.account_id == account.id,
    Position.symbol == symbol
    ).first()
    
    # Buy Trade
    if side == "BUY":
        if account.cash_balance < trade_value:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient funds. Account balance: {account.cash_balance}. Trade Value: {trade_value}"
            )

        account.cash_balance -= trade_value

        if position:
            total_cost = (position.qty * position.avg_cost) + trade_value
            new_qty = position.qty + order_in.quantity
            position.qty = new_qty
            position.avg_cost = total_cost / new_qty
        else:
            position = Position(
                account_id=account.id,
                symbol=symbol,
                qty=order_in.quantity,
                avg_cost=settings.mock_fill_price,
            )
            db.add(position)
    
    # Sell Trade
    elif side == "SELL":
        if not position or position.qty < order_in.quantity:
            raise HTTPException(status_code=400, detail="Not enough shares to sell")

        position.qty -= order_in.quantity
        account.cash_balance += trade_value
    
    db.add(order)
    db.commit()
    db.refresh(position)
    db.refresh(order)

    return order