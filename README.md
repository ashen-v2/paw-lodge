# Paw Lodge

Multi-tenant API for small veterinary practices. Each practice manages its own clients, pets, service prices, visits, vaccinations, and cash payments. A practice only sees its own records.

Login is by email. Email is unique per practice and also globally, so a login always resolves to one user. The authenticated user's practice is the tenant. The API never trusts a practice id sent by the client. A request for another practice's record returns 404.

Visit line items copy the catalog price at the time of the visit. Later price changes do not rewrite old bills. Payments are cash or other. There is no card processing and no AI assistant in this service.

Dates on the dashboard use UTC.

## Stack

Python 3.12, FastAPI, PostgreSQL, SQLAlchemy 2, Alembic, Pydantic v2, JWT, Argon2.

## Run locally

From `backend/`:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Start PostgreSQL. With Docker:

```bash
docker compose up -d db
```

Apply migrations, load the demo clinic, and start the API:

```bash
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

`python -m app.seed` is safe to run again. If the demo owner already exists, it does nothing.

### Demo logins

These passwords are for local development only.

| Name | Email | Password | Role |
| --- | --- | --- | --- |
| Dr. Sarah | sarah@happypaws.example | HappyPaws-Sarah-1 | owner |
| Assistant | assistant@happypaws.example | HappyPaws-Assist-1 | staff |

The owner can update the practice name, phone, and address. Staff can use the clinical records but cannot change practice settings.

The seed clinic is Happy Paws Veterinary Clinic, with owners John, Maria, and David, pets Milo, Luna, and Rocky, and the services Consultation, Rabies Vaccination, Deworming, Wound Dressing, and Nail Clipping.

## Tests

Tests use PostgreSQL, not SQLite, so the queries match the application. Create the database user from `docker compose`, or point `TEST_DATABASE_URL` at a database the tests may create and wipe.

```bash
cd backend
source .venv/bin/activate
pytest
```

The default test database is `postgresql+psycopg://pawlodge:pawlodge@127.0.0.1:5432/pawlodge_test`.

## Docker Compose

From `backend/`:

```bash
cp .env.example .env
# Set JWT_SECRET in .env before sharing this stack. The example value is a placeholder.
docker compose up --build
```

The API container runs `alembic upgrade head` before uvicorn. Compose publishes the API on port 8000 and Postgres on port 5432.

Copy `.env.example` to `.env` for local overrides. Do not commit `.env`.

## Useful routes

- `POST /api/v1/auth/register` creates a practice and its owner user
- `POST /api/v1/auth/login` returns a bearer token
- `GET /api/v1/pets/{pet_id}/history` returns visits, vaccinations, and payments, newest first
- `GET /api/v1/vaccinations/upcoming?days=30` lists due vaccines from today through the given number of days
- `GET /api/v1/analytics/dashboard` returns today's and this month's visits and payment revenue
- `DELETE /api/v1/services/{service_id}` deactivates a service and leaves old visit lines unchanged

Revenue is the sum of payments. Service statistics use the description and subtotal stored on each visit line, not the current catalog price.
