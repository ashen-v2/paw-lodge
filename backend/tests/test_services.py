def test_service_crud_and_deactivate(client, auth_headers, practice):
    created = client.post(
        "/api/v1/services",
        headers=auth_headers,
        json={"name": "Nail Clipping", "price": 500},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["practice_id"] == practice["id"]
    assert body["price"] == 500
    assert body["is_active"] is True
    service_id = body["id"]

    updated = client.patch(
        f"/api/v1/services/{service_id}",
        headers=auth_headers,
        json={"price": 650, "description": "Includes filing"},
    )
    assert updated.status_code == 200
    assert updated.json()["price"] == 650

    deactivated = client.delete(f"/api/v1/services/{service_id}", headers=auth_headers)
    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False

    listed = client.get("/api/v1/services", headers=auth_headers)
    assert service_id not in [item["id"] for item in listed.json()]
    including = client.get("/api/v1/services", headers=auth_headers, params={"include_inactive": True})
    assert service_id in [item["id"] for item in including.json()]
    fetched = client.get(f"/api/v1/services/{service_id}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json()["is_active"] is False


def test_negative_price_is_rejected(client, auth_headers):
    response = client.post(
        "/api/v1/services",
        headers=auth_headers,
        json={"name": "Consultation", "price": -1},
    )
    assert response.status_code == 422
