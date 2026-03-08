from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.orders import OrderCreate, OrderResponse
from app.services import orders

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse)
def market_order(order_in: OrderCreate, db: Session = Depends(get_db)):
    return orders.create_order(db, order_in)