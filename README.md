# Trading Simulator API

A transaction-safe trading order simulation backend built with FastAPI and PostgreSQL.

This project models core backend concepts found in trading systems:

- Market order execution (BUY / SELL)
- Position tracking with weighted average cost
- Cash balance management
- Transaction-safe state updates (ACID compliance)
- Financial precision using Decimal (no floats)

The focus is correctness, relational modeling, and transactional integrity.

---

## Tech Stack

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- Docker & Docker Compose
- Pytest

---

## Architecture


Client → FastAPI → SQLAlchemy → PostgreSQL
|
Transaction Layer


Order execution logic is wrapped in database transactions to ensure atomic state changes.

---

## Data Model

### Users
- Unique email
- One trading account per user (v1 simplification)

### Accounts
- Tracks cash balance
- Enforces non-negative constraint

### Orders
- BUY / SELL
- FILLED or REJECTED
- Stores fill price and rejection reason
- Indexed by account and timestamp

### Positions
- One row per (account, symbol)
- Tracks quantity and weighted average cost
- Unique constraint on (account_id, symbol)

All monetary values use `NUMERIC` in Postgres and Python `Decimal` to prevent floating-point precision errors.

---

## Transaction Safety

Order execution follows this pattern:

1. Lock account row (`SELECT ... FOR UPDATE`)
2. Validate sufficient cash (BUY) or position size (SELL)
3. Update account cash balance
4. Insert or update position (weighted average cost calculation)
5. Insert order record
6. Commit transaction

If validation fails, the transaction rolls back and the order is marked `REJECTED`.

This guarantees atomic and consistent state transitions.

---

## Running Locally

1. Copy environment file:

```bash
cp .env.example .env

Start services:

docker compose up --build

Open API documentation:

http://localhost:8000/docs
Example Usage

Create a user:

curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"me@example.com"}'

Place a BUY order:

curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"account_id":1,"symbol":"AAPL","side":"BUY","qty":"10"}'

Check positions:

curl "http://localhost:8000/positions?account_id=1"
Current Limitations (v1)

Market orders only

Fixed mock fill price

No authentication

No external price feed

No real-time order book

Planned Improvements

External price ingestion

Portfolio valuation endpoint

Realized & unrealized PnL

Order pagination

Background price update jobs

JWT authentication

Alembic migrations

Design Decisions

Why Decimal instead of float?
Financial systems require deterministic precision. Floating-point math introduces rounding errors.

Why unique constraint on positions?
Ensures one row per (account, symbol) and prevents duplicate position state.

Why row-level locking (FOR UPDATE)?
Prevents race conditions during concurrent order execution.

Purpose

This project demonstrates backend engineering fundamentals aligned with trading infrastructure:

Correct financial data handling

Relational schema design

Transaction management

API design best practices

Dockerized development environment
