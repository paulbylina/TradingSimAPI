from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

class HealthResponse(BaseModel):
    ok: bool

class UserCreate(BaseModel):
    email: EmailStr

class UserOut(BaseModel):
    id: int
    email: str
    account_id: int
    cash_balance: Decimal

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

class PositionOut(BaseModel):
    account_id: int
    symbol: str
    qty: Decimal
    avg_cost: Decimal
    
class AccountOut(BaseModel):
    id: int
    user_id: int
    email: str
    cash_balance: Decimal
    created_at: datetime
    