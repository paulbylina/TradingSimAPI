from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel

class PositionOut(BaseModel):
    account_id: int
    symbol: str
    qty: Decimal
    avg_cost: Decimal
    cost_basis: Decimal
    
class AccountOut(BaseModel):
    id: int
    user_id: int
    email: str
    cash_balance: Decimal
    created_at: datetime

class PortfolioOut(BaseModel):
    account_found: bool
    cash_balance: Decimal | None
    positions: list[PositionOut]
    total_cost_basis: Decimal