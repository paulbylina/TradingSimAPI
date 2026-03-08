from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime, ForeignKey, Numeric, CheckConstraint, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.order import Order
    from app.models.position import Position
    from app.models.trade import Trade


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)

    # money -> Numeric with scale
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="account")
    orders: Mapped[list["Order"]] = relationship(back_populates="account")
    positions: Mapped[list["Position"]] = relationship(back_populates="account")
    trades: Mapped[list["Trade"]] = relationship(back_populates="account")

    __table_args__ = (
        CheckConstraint("cash_balance >= 0", name="ck_accounts_cash_nonnegative"),
    )