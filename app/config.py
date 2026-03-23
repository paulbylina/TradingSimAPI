import os
from decimal import Decimal
from pydantic import BaseModel


def _build_database_url() -> str:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url

    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "trading")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


class Settings(BaseModel):
    database_url: str = _build_database_url()
    starting_cash: Decimal = Decimal(os.getenv("STARTING_CASH", "10000.00"))
    mock_fill_price: Decimal = Decimal(os.getenv("MOCK_FILL_PRICE", "100.00"))


settings = Settings()
