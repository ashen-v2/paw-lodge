from datetime import datetime, timedelta, timezone


def test_pet_crud_and_owner_relationship(client, auth_headers, owner, practice):
    created = client.post(
        "/api/v1/pets",
        headers=auth_headers,
        json={
            "owner_id": owner["id"],
            "name": "Luna",
            "species": "Cat",
            "breed": "Domestic Shorthair",
            "sex": "female",
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["owner_id"] == owner["id"]
    assert body["practice_id"] == practice["id"]
    pet_id = body["id"]

    fetched = client.get(f"/api/v1/pets/{pet_id}", headers=auth_headers)
    assert fetched.status_code == 200

    updated = client.patch(
        f"/api/v1/pets/{pet_id}",
        headers=auth_headers,
        json={"color": "black", "notes": "Indoor cat"},
    )
    assert updated.status_code == 200
    assert updated.json()["color"] == "black"
    assert updated.json()["species"] == "Cat"

    deleted = client.delete(f"/api/v1/pets/{pet_id}", headers=auth_headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/pets/{pet_id}", headers=auth_headers).status_code == 404


def test_pet_search_and_species_filter(client, auth_headers, owner):
    client.post(
        "/api/v1/pets",
        headers=auth_headers,
        json={"owner_id": owner["id"], "name": "Milo", "species": "Dog"},
    )
    client.post(
        "/api/v1/pets",
        headers=auth_headers,
        json={"owner_id": owner["id"], "name": "Luna", "species": "Cat"},
    )
    by_name = client.get("/api/v1/pets", headers=auth_headers, params={"search": "mil"})
    assert [pet["name"] for pet in by_name.json()] == ["Milo"]
    by_species = client.get("/api/v1/pets", headers=auth_headers, params={"species": "dog"})
    assert [pet["name"] for pet in by_species.json()] == ["Milo"]


def test_unknown_owner_is_not_found(client, auth_headers):
    response = client.post(
        "/api/v1/pets",
        headers=auth_headers,
        json={
            "owner_id": "00000000-0000-4000-8000-000000000001",
            "name": "Milo",
            "species": "Dog",
        },
    )
    assert response.status_code == 404


def test_pet_history_is_newest_first(client, auth_headers, pet, service):
    today = datetime.now(timezone.utc).date()
    older = today - timedelta(days=10)
    visit = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": older.isoformat(),
            "diagnosis": "General consultation",
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    assert visit.status_code == 201, visit.text
    payment = client.post(
        "/api/v1/payments",
        headers=auth_headers,
        json={
            "visit_id": visit.json()["id"],
            "amount": 1500,
            "payment_method": "cash",
            "paid_at": f"{older.isoformat()}T12:00:00Z",
        },
    )
    assert payment.status_code == 201, payment.text
    vaccination = client.post(
        "/api/v1/vaccinations",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "vaccine_name": "Rabies vaccination",
            "administered_date": today.isoformat(),
            "next_due_date": (today + timedelta(days=365)).isoformat(),
        },
    )
    assert vaccination.status_code == 201, vaccination.text

    history = client.get(f"/api/v1/pets/{pet['id']}/history", headers=auth_headers)
    assert history.status_code == 200
    body = history.json()
    assert body["pet"]["id"] == pet["id"]
    dates = [event["date"] for event in body["timeline"]]
    assert dates == sorted(dates, reverse=True)
    assert body["timeline"][0]["type"] == "vaccination"
    assert body["timeline"][0]["title"] == "Rabies vaccination"
    types = {event["type"] for event in body["timeline"]}
    assert types == {"vaccination", "visit", "payment"}
    visit_event = next(event for event in body["timeline"] if event["type"] == "visit")
    assert visit_event["title"] == "General consultation"
    assert visit_event["details"]["total"] == 1500
