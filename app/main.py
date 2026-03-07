from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, select

from app.db import SessionLocal, engine, Base
from app.models import User, Account, Position, Order
from app.schemas import (
    HealthResponse, UserCreate, UserOut,
    OrderCreate, OrderOut, PositionOut, AccountOut
)
from app.config import settings
from app.services import place_market_order

app = FastAPI(title="Trading Simulator API")

# v1: create tables automatically (swap to Alembic later)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health", response_model=HealthResponse)
def health():
    return {"ok": True}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"ok": True}


@app.post("/users", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(email=str(payload.email))
    db.add(user)
    db.flush()

    acct = Account(user_id=user.id, cash_balance=settings.starting_cash)
    db.add(acct)
    db.commit()
    db.refresh(user)
    db.refresh(acct)

    return UserOut(id=user.id, email=user.email, account_id=acct.id, cash_balance=acct.cash_balance)


@app.get("/positions", response_model=list[PositionOut])
def list_positions(account_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        select(Position).where(Position.account_id == account_id).order_by(Position.symbol.asc())
    ).scalars().all()

    return [
        PositionOut(account_id=r.account_id, symbol=r.symbol, qty=r.qty, avg_cost=r.avg_cost)
        for r in rows
    ]


@app.get("/orders", response_model=list[OrderOut])
def list_orders(account_id: int, limit: int = 50, db: Session = Depends(get_db)):
    rows = db.execute(
        select(Order)
        .where(Order.account_id == account_id)
        .order_by(Order.created_at.desc())
        .limit(min(limit, 200))
    ).scalars().all()

    return [
        OrderOut(
            id=r.id,
            account_id=r.account_id,
            symbol=r.symbol,
            side=r.side,
            qty=r.qty,
            status=r.status,
            filled_price=r.filled_price,
            reject_reason=r.reject_reason,
        )
        for r in rows
    ]


@app.post("/orders", response_model=OrderOut)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    try:
        # Start a transaction explicitly; rollback if anything unexpected happens
        with db.begin():
            order = place_market_order(
                db,
                account_id=payload.account_id,
                symbol=payload.symbol,
                side=payload.side,
                qty=payload.qty,
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Order processing error: {e}")

    return OrderOut(
        id=order.id,
        account_id=order.account_id,
        symbol=order.symbol,
        side=order.side,
        qty=order.qty,
        status=order.status,
        filled_price=order.filled_price,
        reject_reason=order.reject_reason,
    )
    

@app.get("/accounts/{account_id}", response_model=AccountOut)
def get_account(account_id: int, db: Session = Depends(get_db)):
    acct = db.execute(
        select(Account).where(Account.id == account_id)
    ).scalar_one_or_none()

    if not acct:
        raise HTTPException(status_code=404, detail="Account not found")
    
    user = db.execute(
        select(User).where(User.id == acct.user_id)
    ).scalar_one()

    return AccountOut(
        id=acct.id,
        user_id=acct.user_id,
        email=user.email,
        cash_balance=acct.cash_balance,
        created_at=acct.created_at,
    )
    
