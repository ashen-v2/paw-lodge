from uuid import UUID

from app.core.security import hash_password
from app.models.user import ROLE_STAFF, User


def _staff_headers(client, db_session, sarah):
    db_session.add(
        User(
            practice_id=UUID(sarah["user"]["practice_id"]),
            name="Assistant",
            email="assistant@example.com",
            password_hash=hash_password("password123"),
            role=ROLE_STAFF,
        )
    )
    db_session.commit()
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "assistant@example.com", "password": "password123"},
    )
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_get_practice(client, auth_headers, practice, user):
    assert practice["name"] == "Happy Paws Veterinary Clinic"
    assert practice["id"] == user["practice_id"]
    assert practice["phone"] is None


def test_owner_can_update_practice(client, auth_headers):
    response = client.patch(
        "/api/v1/practice",
        headers=auth_headers,
        json={"name": "Happy Paws", "phone": "555-0199", "address": "12 Clinic Lane"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Happy Paws"
    assert body["phone"] == "555-0199"
    assert body["address"] == "12 Clinic Lane"


def test_staff_can_read_but_not_update_practice(client, db_session, sarah):
    headers = _staff_headers(client, db_session, sarah)
    read = client.get("/api/v1/practice", headers=headers)
    assert read.status_code == 200
    update = client.patch("/api/v1/practice", headers=headers, json={"name": "Taken Over"})
    assert update.status_code == 403
    unchanged = client.get("/api/v1/practice", headers=headers)
    assert unchanged.json()["name"] == "Happy Paws Veterinary Clinic"
