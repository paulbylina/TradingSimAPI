from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class OrderCreate(BaseModel):
    user_id: int
    symbol: str = Field(..., min_length=1, max_length=16)
    side: str
    quantity: int = Field(..., gt=0)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str) -> str:
        return value.upper()

    @field_validator("side")
    @classmethod
    def validate_side(cls, value: str) -> str:
        value = value.lower()
        if value not in {"buy", "sell"}:
            raise ValueError("side must be 'buy' or 'sell'")
        return value
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "symbol": "AAPL",
                "side": "buy",
                "quantity": 10
            }
        }
    }


class OrderResponse(BaseModel):
    id: int
    user_id: int
    symbol: str
    side: str
    quantity: int
    price: Decimal

    model_config = {
        "from_attributes": True,
    }