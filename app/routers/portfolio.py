from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.account import Account
from app.models.position import Position
from app.schemas.portfolio import PortfolioOut

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("", response_model=PortfolioOut)
def get_portfolio(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    positions = db.query(Position).filter(Position.account_id == account_id).all()
    total_cost_basis = round(sum(p.qty * p.avg_cost for p in positions), 2)
    return {
        "account_found": account is not None,
        "cash_balance": account.cash_balance if account else None,
        "positions": [
            {
                "account_id": p.account_id,
                "symbol": p.symbol,
                "qty": round(p.qty, 2),
                "avg_cost": round(p.avg_cost, 2),
                "cost_basis": round(p.qty * p.avg_cost, 2)
            }
            for p in positions
        ],
        "total_cost_basis": total_cost_basis
    }