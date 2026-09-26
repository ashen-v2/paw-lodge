import os

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://pawlodge:pawlodge@127.0.0.1:5432/pawlodge_test",
)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["JWT_SECRET"] = "test-secret-not-for-production-use"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.core.database import Base, get_db, register_utc_listener
from app.main import app

PASSWORD = "password123"


def _ensure_database() -> None:
    database_name = TEST_DATABASE_URL.rsplit("/", 1)[1]
    admin_url = TEST_DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
    admin = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": database_name},
            ).scalar()
            if not exists:
                connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    finally:
        admin.dispose()


@pytest.fixture(scope="session")
def engine():
    try:
        _ensure_database()
    except Exception as exc:
        pytest.exit(
            "Tests require PostgreSQL. Start it with docker compose or set TEST_DATABASE_URL. "
            f"Connection failed: {exc}",
            returncode=1,
        )
    bound = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    register_utc_listener(bound)
    Base.metadata.drop_all(bound)
    Base.metadata.create_all(bound)
    yield bound
    bound.dispose()


@pytest.fixture
def db_session(engine) -> Generator[Session, None, None]:
    session = Session(bind=engine, autoflush=False, expire_on_commit=False)
    try:
        yield session
    finally:
        session.close()
        table_list = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
        with engine.begin() as connection:
            connection.execute(text(f"TRUNCATE {table_list} RESTART IDENTITY CASCADE"))


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def register_practice(
    client: TestClient,
    email: str,
    *,
    practice_name: str = "Happy Paws Veterinary Clinic",
    name: str = "Dr. Sarah",
    password: str = PASSWORD,
) -> dict:
    created = client.post(
        "/api/v1/auth/register",
        json={
            "practice_name": practice_name,
            "name": name,
            "email": email,
            "password": password,
        },
    )
    assert created.status_code == 201, created.text
    logged_in = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert logged_in.status_code == 200, logged_in.text
    token = logged_in.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200, me.text
    return {
        "headers": headers,
        "user": me.json(),
        "email": email,
        "password": password,
        "token": token,
        "registered": created.json(),
    }


@pytest.fixture
def sarah(client: TestClient) -> dict:
    return register_practice(client, "sarah@example.com")


@pytest.fixture
def auth_headers(sarah: dict) -> dict:
    return sarah["headers"]


@pytest.fixture
def user(sarah: dict) -> dict:
    return sarah["user"]


@pytest.fixture
def practice(client: TestClient, auth_headers: dict) -> dict:
    response = client.get("/api/v1/practice", headers=auth_headers)
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture
def other_practice(client: TestClient) -> dict:
    return register_practice(
        client,
        "other@example.com",
        practice_name="Second Street Clinic",
        name="Dr. Lee",
    )


@pytest.fixture
def other_headers(other_practice: dict) -> dict:
    return other_practice["headers"]


@pytest.fixture
def owner(client: TestClient, auth_headers: dict) -> dict:
    response = client.post(
        "/api/v1/owners",
        headers=auth_headers,
        json={
            "name": "John",
            "phone": "555-0101",
            "email": "john@example.com",
            "address": "1 Oak Street",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def pet(client: TestClient, auth_headers: dict, owner: dict) -> dict:
    response = client.post(
        "/api/v1/pets",
        headers=auth_headers,
        json={
            "owner_id": owner["id"],
            "name": "Milo",
            "species": "Dog",
            "breed": "Golden Retriever",
            "sex": "male",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def service(client: TestClient, auth_headers: dict) -> dict:
    response = client.post(
        "/api/v1/services",
        headers=auth_headers,
        json={"name": "Consultation", "description": "General consult", "price": 1500},
    )
    assert response.status_code == 201, response.text
    return response.json()
