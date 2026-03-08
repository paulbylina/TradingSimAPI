from fastapi import APIRouter

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("")
def portfolio_check():
    return {"status": "portfolio ok"}