from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.routers import all_routers
from app.db import get_db

app = FastAPI(title="Trading Simulator API")

for router in all_routers:
    app.include_router(router)

@app.get("/")
def root():
    return {"message": "Trading Simulator API is running"}

@app.get("/health")
def db_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"ok": "Health OK"}