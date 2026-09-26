from datetime import datetime, timedelta, timezone


def test_create_list_and_pet_vaccinations(client, auth_headers, pet):
    today = datetime.now(timezone.utc).date()
    created = client.post(
        "/api/v1/vaccinations",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "vaccine_name": "Rabies",
            "administered_date": today.isoformat(),
            "next_due_date": (today + timedelta(days=365)).isoformat(),
            "batch_number": "RB-1",
        },
    )
    assert created.status_code == 201, created.text
    vaccination_id = created.json()["id"]
    assert created.json()["pet_id"] == pet["id"]

    listed = client.get("/api/v1/vaccinations", headers=auth_headers)
    assert [item["id"] for item in listed.json()] == [vaccination_id]
    for_pet = client.get(f"/api/v1/pets/{pet['id']}/vaccinations", headers=auth_headers)
    assert [item["id"] for item in for_pet.json()] == [vaccination_id]

    updated = client.patch(
        f"/api/v1/vaccinations/{vaccination_id}",
        headers=auth_headers,
        json={"notes": "Left shoulder"},
    )
    assert updated.status_code == 200
    assert updated.json()["notes"] == "Left shoulder"

    deleted = client.delete(f"/api/v1/vaccinations/{vaccination_id}", headers=auth_headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/vaccinations/{vaccination_id}", headers=auth_headers).status_code == 404


def test_due_date_cannot_precede_administration(client, auth_headers, pet):
    response = client.post(
        "/api/v1/vaccinations",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "vaccine_name": "Rabies",
            "administered_date": "2026-09-26",
            "next_due_date": "2026-09-01",
        },
    )
    assert response.status_code == 422


def test_upcoming_vaccinations(client, auth_headers, pet):
    today = datetime.now(timezone.utc).date()
    due_soon = today + timedelta(days=7)
    due_later = today + timedelta(days=45)
    overdue = today - timedelta(days=1)
    for name, due in (("Soon", due_soon), ("Later", due_later), ("Overdue", overdue)):
        created = client.post(
            "/api/v1/vaccinations",
            headers=auth_headers,
            json={
                "pet_id": pet["id"],
                "vaccine_name": name,
                "administered_date": (today - timedelta(days=30)).isoformat(),
                "next_due_date": due.isoformat(),
            },
        )
        assert created.status_code == 201, created.text

    upcoming = client.get("/api/v1/vaccinations/upcoming", headers=auth_headers, params={"days": 30})
    assert upcoming.status_code == 200
    assert [item["vaccine_name"] for item in upcoming.json()] == ["Soon"]
