from uuid import UUID

import jwt

from app.models.user import User
from tests.conftest import PASSWORD, register_practice


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_creates_practice_owner(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "practice_name": "Happy Paws Veterinary Clinic",
            "name": "Dr. Sarah",
            "email": "Sarah@Example.com",
            "password": PASSWORD,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "sarah@example.com"
    assert body["role"] == "owner"
    assert body["is_active"] is True
    assert "password" not in response.text
    assert "password_hash" not in response.text

    practice = client.post(
        "/api/v1/auth/login",
        json={"email": "sarah@example.com", "password": PASSWORD},
    )
    token = practice.json()["access_token"]
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    clinic = client.get("/api/v1/practice", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert clinic.json()["name"] == "Happy Paws Veterinary Clinic"
    assert clinic.json()["id"] == body["practice_id"]


def test_register_rejects_duplicate_email(client):
    register_practice(client, "sarah@example.com")
    duplicate = client.post(
        "/api/v1/auth/register",
        json={
            "practice_name": "Another Clinic",
            "name": "Someone",
            "email": "SARAH@example.com",
            "password": PASSWORD,
        },
    )
    assert duplicate.status_code == 409


def test_register_rejects_short_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "practice_name": "Happy Paws Veterinary Clinic",
            "name": "Dr. Sarah",
            "email": "sarah@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 422


def test_login_and_token_claims(client, sarah):
    payload = jwt.decode(sarah["token"], "test-secret-not-for-production-use", algorithms=["HS256"])
    assert payload["user_id"] == sarah["user"]["id"]
    assert payload["practice_id"] == sarah["user"]["practice_id"]
    assert payload["role"] == "owner"
    assert "email" not in payload
    assert "password" not in payload


def test_login_rejects_invalid_password(client, sarah):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": sarah["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_rejects_unknown_email(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": PASSWORD},
    )
    assert response.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.get("/api/v1/owners", headers={"Authorization": "Bearer not-a-token"}).status_code == 401


def test_inactive_user_is_rejected(client, db_session, sarah):
    account = db_session.get(User, UUID(sarah["user"]["id"]))
    account.is_active = False
    db_session.commit()

    me = client.get("/api/v1/auth/me", headers=sarah["headers"])
    assert me.status_code == 401
    assert me.json()["detail"] == "User account is inactive"

    login = client.post(
        "/api/v1/auth/login",
        json={"email": sarah["email"], "password": sarah["password"]},
    )
    assert login.status_code == 401
    assert login.json()["detail"] == "User account is inactive"
