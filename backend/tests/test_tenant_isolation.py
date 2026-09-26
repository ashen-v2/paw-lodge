from uuid import uuid4


def _assert_hidden(client, headers, path):
    fetched = client.get(path, headers=headers)
    assert fetched.status_code == 404
    assert "practice" not in fetched.json()["detail"].lower()
    patched = client.patch(path, headers=headers, json={"name": "Stolen"})
    assert patched.status_code == 404
    deleted = client.delete(path, headers=headers)
    assert deleted.status_code == 404


def test_owners_are_isolated(client, auth_headers, other_headers, owner):
    _assert_hidden(client, other_headers, f"/api/v1/owners/{owner['id']}")
    listed = client.get("/api/v1/owners", headers=other_headers)
    assert listed.json() == []


def test_pets_are_isolated(client, auth_headers, other_headers, pet):
    _assert_hidden(client, other_headers, f"/api/v1/pets/{pet['id']}")
    assert client.get("/api/v1/pets", headers=other_headers).json() == []
    history = client.get(f"/api/v1/pets/{pet['id']}/history", headers=other_headers)
    assert history.status_code == 404


def test_services_are_isolated(client, auth_headers, other_headers, service):
    _assert_hidden(client, other_headers, f"/api/v1/services/{service['id']}")
    assert client.get("/api/v1/services", headers=other_headers).json() == []


def test_visits_are_isolated(client, auth_headers, other_headers, pet, service):
    created = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-26",
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    assert created.status_code == 201, created.text
    visit_id = created.json()["id"]
    assert client.get(f"/api/v1/visits/{visit_id}", headers=other_headers).status_code == 404
    assert client.patch(
        f"/api/v1/visits/{visit_id}",
        headers=other_headers,
        json={"notes": "nope"},
    ).status_code == 404
    assert client.delete(f"/api/v1/visits/{visit_id}", headers=other_headers).status_code == 404
    assert client.get("/api/v1/visits", headers=other_headers).json() == []

    stolen_pet = client.post(
        "/api/v1/visits",
        headers=other_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-26",
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    assert stolen_pet.status_code == 404


def test_vaccinations_are_isolated(client, auth_headers, other_headers, pet):
    created = client.post(
        "/api/v1/vaccinations",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "vaccine_name": "Rabies",
            "administered_date": "2026-09-26",
        },
    )
    vaccination_id = created.json()["id"]
    assert client.get(f"/api/v1/vaccinations/{vaccination_id}", headers=other_headers).status_code == 404
    assert client.patch(
        f"/api/v1/vaccinations/{vaccination_id}",
        headers=other_headers,
        json={"notes": "nope"},
    ).status_code == 404
    assert client.delete(f"/api/v1/vaccinations/{vaccination_id}", headers=other_headers).status_code == 404
    assert client.get("/api/v1/vaccinations", headers=other_headers).json() == []
    assert client.get(f"/api/v1/pets/{pet['id']}/vaccinations", headers=other_headers).status_code == 404


def test_payments_are_isolated(client, auth_headers, other_headers, pet, service):
    visit = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-26",
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    visit_id = visit.json()["id"]
    payment = client.post(
        "/api/v1/payments",
        headers=auth_headers,
        json={"visit_id": visit_id, "amount": 1500, "payment_method": "cash"},
    )
    assert payment.status_code == 201, payment.text
    assert client.get(f"/api/v1/visits/{visit_id}/payment", headers=other_headers).status_code == 404
    stolen = client.post(
        "/api/v1/payments",
        headers=other_headers,
        json={"visit_id": visit_id, "amount": 1500, "payment_method": "cash"},
    )
    assert stolen.status_code == 404
    assert client.get("/api/v1/payments", headers=other_headers).json() == []
    assert client.get(f"/api/v1/visits/{uuid4()}/payment", headers=auth_headers).status_code == 404
