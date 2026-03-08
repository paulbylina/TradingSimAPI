from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    String, DateTime, ForeignKey, Numeric, CheckConstraint, Index, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.trade import Trade

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)

    symbol: Mapped[str] = mapped_column(String(32), index=True)
    side: Mapped[str] = mapped_column(String(4))  # BUY/SELL
    qty: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)

    status: Mapped[str] = mapped_column(String(16))  # FILLED/REJECTED
    filled_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    reject_reason: Mapped[str | None] = mapped_column(String(300), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    account: Mapped["Account"] = relationship(back_populates="orders")
    trades: Mapped[list["Trade"]] = relationship(back_populates="order")

    __table_args__ = (
        CheckConstraint("qty > 0", name="ck_orders_qty_positive"),
        CheckConstraint("side in ('BUY','SELL')", name="ck_orders_side_valid"),
        Index("ix_orders_account_created", "account_id", "created_at"),
    )