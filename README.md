# Customer API

A FastAPI service for managing customer records, with API-key protection, database
migrations, an HMAC-signed webhook receiver and an automated test suite.

## Features

- Full CRUD for customers with pagination (`page`, `per_page`)
- `X-API-Key` header protection on every `/customers` endpoint (401 missing, 403 wrong)
- Proper error handling: 404 for unknown ids, 409 for duplicate emails, 422 for invalid input
- Webhook receiver `POST /webhooks/customer-events` verified with HMAC-SHA256, processed in the background
- SQLAlchemy 2.0 models, Alembic migrations, Pydantic v2 schemas
- `GET /health` that checks the database connection
- Integration tests with a separate test database and coverage reporting

## Tech stack

Python, FastAPI, SQLAlchemy, Alembic, PostgreSQL (pg8000 driver), Pydantic, pytest, pytest-cov

## Project structure

```
customer_api/
├── src/
│   ├── main.py          # app, router registration, /health
│   ├── config.py        # reads settings from .env
│   ├── database.py      # engine, session, get_db dependency
│   ├── models.py        # Customer model
│   ├── schemas.py       # CustomerCreate / CustomerUpdate / CustomerOut / CustomerPage
│   ├── security.py      # verify_api_key dependency
│   ├── customers.py     # CRUD endpoints
│   └── webhooks.py      # HMAC-verified webhook endpoint
├── tests/               # pytest integration tests (separate SQLite test database)
├── scripts/
│   └── send_webhook.py  # signs and posts valid / tampered / unsigned payloads
├── alembic/             # migrations
├── .env.example
├── .gitignore
└── pyproject.toml
```

## Setup

1. Create a PostgreSQL database named `customer_db`.
2. Create and activate a virtual environment, then install the dependencies:

   ```
   python -m venv venv
   venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
   python -m pip install fastapi uvicorn sqlalchemy alembic pg8000 python-dotenv "pydantic[email]" pytest pytest-cov httpx
   ```
3. Copy `.env.example` to `.env` and fill in real values:

   ```
   DATABASE_URL=postgresql+pg8000://postgres:YOUR_PASSWORD@localhost:5432/customer_db
   API_KEY=a-long-random-string
   WEBHOOK_SECRET=another-long-random-string
   ```
4. Apply the migrations:

   ```
   python -m alembic upgrade head
   ```

## Run

```
python -m uvicorn src.main:app --port 8000
```

Interactive docs are at <http://127.0.0.1:8000/docs>. Click **Authorize** and enter your
`API_KEY` to try the protected endpoints.

## API

| Method | Path | Description | Success | Errors |
|---|---|---|---|---|
| GET | `/health` | Liveness and database check (no key needed) | 200 | 503 |
| POST | `/customers` | Create a customer | 201 | 401, 403, 409, 422 |
| GET | `/customers?page=1&per_page=10` | List customers (paginated) | 200 | 401, 403, 422 |
| GET | `/customers/{id}` | Get one customer | 200 | 401, 403, 404 |
| PUT | `/customers/{id}` | Update a customer (partial update) | 200 | 401, 403, 404, 409, 422 |
| DELETE | `/customers/{id}` | Delete a customer | 204 | 401, 403, 404 |
| POST | `/webhooks/customer-events` | Receive a signed event | 200 | 401 |

Send the key in the `X-API-Key` header:

```
curl.exe -H "X-API-Key: YOUR_API_KEY" "http://127.0.0.1:8000/customers?page=1&per_page=10"
```

## Webhook signature

The sender computes `HMAC-SHA256(raw_body, WEBHOOK_SECRET)` and sends the hex digest in the
`X-Signature` header (a `sha256=` prefix is also accepted). The server recomputes the
signature over the raw request body and compares it with `hmac.compare_digest`. A missing or
wrong signature returns 401. A valid one returns `{"status": "accepted"}` immediately and the
event is processed afterwards with `BackgroundTasks`.

Try it against a running server:

```
python scripts\send_webhook.py
```

## Tests

The tests use FastAPI's `TestClient` and a separate SQLite test database that is recreated for
every test, so your real data is never touched.

```
python -m pytest -v
python -m pytest --cov=src --cov-report=term-missing
```

Coverage is reported for `src/`. The only uncovered line is the PostgreSQL engine branch in
`database.py`, because the tests run on SQLite.

## Design notes

- One database session per request through the `get_db` dependency, always closed afterwards.
- The API-key check is a single reusable dependency attached to the customers router.
- Secrets live in `.env`, which is git-ignored; `.env.example` shows the required variables.
- Webhook signatures are verified against the raw bytes of the body and compared in constant time.
