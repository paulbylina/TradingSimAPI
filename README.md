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


## Project Structure

```
trading-sim-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   └── services.py
├── tests/
│   └── test_orders.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

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
```

2. Start services:

```bash
docker compose up --build
```

3. Open API documentation:

```text
http://localhost:8000/docs
```

### Common DB auth issue

If you see this error:

```text
psycopg2.OperationalError: FATAL: password authentication failed for user "postgres"
```

it means your app credentials do not match the running database credentials.

- If running with Docker Compose, this project expects `postgres/postgres` by default.
- If your local Postgres uses a different password, update `DATABASE_URL` (or `POSTGRES_*` values) in `.env`.
- If you changed DB credentials in Docker previously, recreate volumes:

```bash
docker compose down -v
docker compose up --build
```

## Example Usage

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
