from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

class OrderCreate(BaseModel):
    account_id: int
    symbol: str = Field(min_length=1, max_length=32)
    side: str = Field(pattern="^(BUY|SELL)$")
    qty: Decimal = Field(gt=0)

class OrderOut(BaseModel):
    id: int
    account_id: int
    symbol: str
    side: str
    qty: Decimal
    status: str
    filled_price: Decimal | None
    reject_reason: str | None