import os
from decimal import Decimal
from pydantic import BaseModel

class Settings(BaseModel):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/trading",
    )
    starting_cash: Decimal = Decimal(os.getenv("STARTING_CASH", "10000.00"))
    mock_fill_price: Decimal = Decimal(os.getenv("MOCK_FILL_PRICE", "100.00"))

settings = Settings()