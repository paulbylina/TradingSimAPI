from .portfolio import router as portfolio_router
from .orders import router as order_router

all_routers = [
    portfolio_router,
    order_router
]