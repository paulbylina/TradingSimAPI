from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.user import User
from app.models.account import Account


def seed():
    db: Session = SessionLocal()

    try:
        # check if user already exists
        existing = db.query(User).filter(User.email == "demo@trading.com").first()

        if existing:
            print("Seed data already exists")
            return

        # create user
        user = User(email="demo@trading.com")
        db.add(user)
        db.flush()  # gets user.id without committing

        # create account
        account = Account(
            user_id=user.id,
            cash_balance=100000
        )

        db.add(account)

        db.commit()

        print("Seed data created successfully")

    finally:
        db.close()


if __name__ == "__main__":
    seed()