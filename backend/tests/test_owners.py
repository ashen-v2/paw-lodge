def test_owner_crud(client, auth_headers, practice):
    created = client.post(
        "/api/v1/owners",
        headers=auth_headers,
        json={"name": "Maria", "phone": "555-0102", "email": "Maria@Example.com"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["practice_id"] == practice["id"]
    assert body["email"] == "maria@example.com"
    owner_id = body["id"]

    fetched = client.get(f"/api/v1/owners/{owner_id}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Maria"

    updated = client.patch(
        f"/api/v1/owners/{owner_id}",
        headers=auth_headers,
        json={"phone": "555-0199", "address": "8 River Road"},
    )
    assert updated.status_code == 200
    assert updated.json()["phone"] == "555-0199"
    assert updated.json()["name"] == "Maria"

    deleted = client.delete(f"/api/v1/owners/{owner_id}", headers=auth_headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/owners/{owner_id}", headers=auth_headers).status_code == 404


def test_owner_search(client, auth_headers):
    client.post("/api/v1/owners", headers=auth_headers, json={"name": "Maria Lopez", "phone": "555-0102"})
    client.post("/api/v1/owners", headers=auth_headers, json={"name": "John", "phone": "555-0101"})
    response = client.get("/api/v1/owners", headers=auth_headers, params={"search": "maria"})
    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == ["Maria Lopez"]


def test_owner_rejects_client_practice_id(client, auth_headers, practice):
    response = client.post(
        "/api/v1/owners",
        headers=auth_headers,
        json={"name": "John", "phone": "555-0101", "practice_id": practice["id"]},
    )
    assert response.status_code == 422


def test_cannot_delete_owner_with_pets(client, auth_headers, owner, pet):
    response = client.delete(f"/api/v1/owners/{owner['id']}", headers=auth_headers)
    assert response.status_code == 400


def test_owners_require_auth(client):
    assert client.get("/api/v1/owners").status_code == 401
