def _visit(client, headers, pet, service, day="2026-09-26"):
    response = client.post(
        "/api/v1/visits",
        headers=headers,
        json={
            "pet_id": pet["id"],
            "visit_date": day,
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_record_payment_and_outstanding(client, auth_headers, pet, service):
    visit = _visit(client, auth_headers, pet, service)
    partial = client.post(
        "/api/v1/payments",
        headers=auth_headers,
        json={"visit_id": visit["id"], "amount": 500, "payment_method": "cash"},
    )
    assert partial.status_code == 201, partial.text
    assert partial.json()["amount"] == 500
    assert partial.json()["payment_method"] == "cash"

    fetched = client.get(f"/api/v1/visits/{visit['id']}/payment", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json()["id"] == partial.json()["id"]

    refreshed = client.get(f"/api/v1/visits/{visit['id']}", headers=auth_headers)
    assert refreshed.json()["total"] == 1500
    assert refreshed.json()["outstanding"] == 1000

    listed = client.get("/api/v1/payments", headers=auth_headers)
    assert [item["id"] for item in listed.json()] == [partial.json()["id"]]


def test_payment_cannot_exceed_visit_total(client, auth_headers, pet, service):
    visit = _visit(client, auth_headers, pet, service)
    response = client.post(
        "/api/v1/payments",
        headers=auth_headers,
        json={"visit_id": visit["id"], "amount": 1500.01, "payment_method": "cash"},
    )
    assert response.status_code == 400


def test_payment_amount_must_be_positive(client, auth_headers, pet, service):
    visit = _visit(client, auth_headers, pet, service)
    response = client.post(
        "/api/v1/payments",
        headers=auth_headers,
        json={"visit_id": visit["id"], "amount": 0, "payment_method": "other"},
    )
    assert response.status_code == 422


def test_one_payment_per_visit(client, auth_headers, pet, service):
    visit = _visit(client, auth_headers, pet, service)
    first = client.post(
        "/api/v1/payments",
        headers=auth_headers,
        json={"visit_id": visit["id"], "amount": 1500, "payment_method": "cash"},
    )
    assert first.status_code == 201
    second = client.post(
        "/api/v1/payments",
        headers=auth_headers,
        json={"visit_id": visit["id"], "amount": 100, "payment_method": "cash"},
    )
    assert second.status_code == 409
    refreshed = client.get(f"/api/v1/visits/{visit['id']}", headers=auth_headers)
    assert refreshed.json()["outstanding"] == 0
