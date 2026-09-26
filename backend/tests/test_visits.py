from uuid import uuid4


def test_visit_with_multiple_items_calculates_total(client, auth_headers, pet, service):
    deworming = client.post(
        "/api/v1/services",
        headers=auth_headers,
        json={"name": "Deworming", "price": 800},
    )
    assert deworming.status_code == 201
    response = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-26",
            "notes": "Routine consultation",
            "items": [
                {"service_id": service["id"], "quantity": 1},
                {"service_id": deworming.json()["id"], "quantity": 2},
            ],
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["user_id"]
    assert [item["subtotal"] for item in body["items"]] == [1500, 1600]
    assert body["total"] == 3100
    assert body["outstanding"] == 3100
    assert body["payment"] is None

    listed = client.get(f"/api/v1/pets/{pet['id']}/visits", headers=auth_headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [body["id"]]


def test_historical_price_snapshot(client, auth_headers, pet):
    created = client.post(
        "/api/v1/services",
        headers=auth_headers,
        json={"name": "Consultation", "price": 1500},
    )
    service_id = created.json()["id"]
    first = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-01",
            "items": [{"service_id": service_id, "quantity": 1}],
        },
    )
    assert first.status_code == 201, first.text
    visit_id = first.json()["id"]

    changed = client.patch(
        f"/api/v1/services/{service_id}",
        headers=auth_headers,
        json={"price": 2000},
    )
    assert changed.json()["price"] == 2000

    stored = client.get(f"/api/v1/visits/{visit_id}", headers=auth_headers)
    assert stored.status_code == 200
    assert stored.json()["items"][0]["unit_price"] == 1500
    assert stored.json()["items"][0]["subtotal"] == 1500
    assert stored.json()["total"] == 1500

    second = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-20",
            "items": [{"service_id": service_id, "quantity": 1}],
        },
    )
    assert second.status_code == 201, second.text
    assert second.json()["items"][0]["unit_price"] == 2000
    assert second.json()["total"] == 2000


def test_one_off_item_and_client_total_is_rejected(client, auth_headers, pet, service):
    rejected = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-26",
            "total": 1,
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    assert rejected.status_code == 422

    created = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-26",
            "items": [
                {"service_id": service["id"], "quantity": 1},
                {"description": "Custom supplement", "quantity": 3, "unit_price": 300},
            ],
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["items"][1]["service_id"] is None
    assert body["items"][1]["subtotal"] == 900
    assert body["total"] == 2400


def test_invalid_pet_and_service(client, auth_headers, pet, service):
    missing_pet = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": str(uuid4()),
            "visit_date": "2026-09-26",
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    assert missing_pet.status_code == 404

    missing_service = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-26",
            "items": [{"service_id": str(uuid4()), "quantity": 1}],
        },
    )
    assert missing_service.status_code == 404

    zero_quantity = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-26",
            "items": [{"service_id": service["id"], "quantity": 0}],
        },
    )
    assert zero_quantity.status_code == 422


def test_inactive_service_cannot_be_added_but_history_remains(client, auth_headers, pet, service):
    created = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-10",
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    visit_id = created.json()["id"]
    assert client.delete(f"/api/v1/services/{service['id']}", headers=auth_headers).status_code == 200
    stored = client.get(f"/api/v1/visits/{visit_id}", headers=auth_headers)
    assert stored.json()["items"][0]["unit_price"] == 1500
    assert stored.json()["items"][0]["service_id"] == service["id"]

    rejected = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-11",
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    assert rejected.status_code == 400


def test_update_and_delete_visit(client, auth_headers, pet, service):
    created = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-26",
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    visit_id = created.json()["id"]
    updated = client.patch(
        f"/api/v1/visits/{visit_id}",
        headers=auth_headers,
        json={"diagnosis": "Healthy", "notes": "No treatment"},
    )
    assert updated.status_code == 200
    assert updated.json()["diagnosis"] == "Healthy"
    assert updated.json()["total"] == 1500

    deleted = client.delete(f"/api/v1/visits/{visit_id}", headers=auth_headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/visits/{visit_id}", headers=auth_headers).status_code == 404


def test_cannot_delete_pet_with_visit(client, auth_headers, pet, service):
    created = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-26",
            "items": [],
        },
    )
    assert created.status_code == 201
    assert client.delete(f"/api/v1/pets/{pet['id']}", headers=auth_headers).status_code == 400
