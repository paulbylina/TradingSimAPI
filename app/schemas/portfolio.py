from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel

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
    