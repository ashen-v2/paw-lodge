from datetime import datetime, time, timedelta, timezone


def _today():
    return datetime.now(timezone.utc).date()


def _pet(client, headers, owner, name="Milo"):
    response = client.post(
        "/api/v1/pets",
        headers=headers,
        json={"owner_id": owner["id"], "name": name, "species": "Dog"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _service(client, headers, name, price):
    response = client.post(
        "/api/v1/services",
        headers=headers,
        json={"name": name, "price": price},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_dashboard_today_and_month(client, auth_headers, owner):
    today = _today()
    previous = today.replace(day=1) - timedelta(days=1)
    pet = _pet(client, auth_headers, owner)
    service = _service(client, auth_headers, "Consultation", 100)

    current = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": today.isoformat(),
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    assert current.status_code == 201, current.text
    paid = client.post(
        "/api/v1/payments",
        headers=auth_headers,
        json={"visit_id": current.json()["id"], "amount": 100, "payment_method": "cash"},
    )
    assert paid.status_code == 201, paid.text

    earlier = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": previous.isoformat(),
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    assert earlier.status_code == 201, earlier.text
    earlier_paid = client.post(
        "/api/v1/payments",
        headers=auth_headers,
        json={
            "visit_id": earlier.json()["id"],
            "amount": 100,
            "payment_method": "cash",
            "paid_at": datetime.combine(previous, time(12, 0), tzinfo=timezone.utc).isoformat(),
        },
    )
    assert earlier_paid.status_code == 201, earlier_paid.text

    this_month = client.post(
        "/api/v1/vaccinations",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "vaccine_name": "Rabies",
            "administered_date": today.isoformat(),
            "next_due_date": (today + timedelta(days=10)).isoformat(),
        },
    )
    assert this_month.status_code == 201, this_month.text
    client.post(
        "/api/v1/vaccinations",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "vaccine_name": "Old",
            "administered_date": previous.isoformat(),
            "next_due_date": (today + timedelta(days=40)).isoformat(),
        },
    )

    dashboard = client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    assert dashboard.status_code == 200, dashboard.text
    body = dashboard.json()
    assert body["today"] == {"visits": 1, "revenue": 100}
    assert body["month"]["visits"] == 1
    assert body["month"]["revenue"] == 100
    assert body["month"]["new_pets"] == 1
    assert body["month"]["vaccinations"] == 1
    assert body["upcoming_vaccinations"] == 1


def test_revenue_series(client, auth_headers, owner):
    today = _today()
    pet = _pet(client, auth_headers, owner)
    service = _service(client, auth_headers, "Consultation", 5200)
    visit = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": today.isoformat(),
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    client.post(
        "/api/v1/payments",
        headers=auth_headers,
        json={"visit_id": visit.json()["id"], "amount": 5200, "payment_method": "cash"},
    )
    response = client.get(
        "/api/v1/analytics/revenue",
        headers=auth_headers,
        params={"from": today.isoformat(), "to": today.isoformat()},
    )
    assert response.status_code == 200
    assert response.json() == [{"date": today.isoformat(), "revenue": 5200}]

    invalid = client.get(
        "/api/v1/analytics/revenue",
        headers=auth_headers,
        params={"from": today.isoformat(), "to": (today - timedelta(days=1)).isoformat()},
    )
    assert invalid.status_code == 400


def test_service_statistics_use_snapshots(client, auth_headers, pet):
    consultation = _service(client, auth_headers, "Consultation", 1500)
    vaccination = _service(client, auth_headers, "Rabies Vaccination", 2500)
    created = client.post(
        "/api/v1/visits",
        headers=auth_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": "2026-09-15",
            "items": [
                {"service_id": consultation["id"], "quantity": 1},
                {"service_id": vaccination["id"], "quantity": 2},
                {"description": "House call", "quantity": 1, "unit_price": 400},
            ],
        },
    )
    assert created.status_code == 201, created.text
    client.patch(
        f"/api/v1/services/{consultation['id']}",
        headers=auth_headers,
        json={"price": 9999},
    )
    response = client.get(
        "/api/v1/analytics/services",
        headers=auth_headers,
        params={"from": "2026-09-01", "to": "2026-09-30"},
    )
    assert response.status_code == 200
    by_name = {row["service"]: row for row in response.json()}
    assert by_name["Consultation"] == {"service": "Consultation", "count": 1, "revenue": 1500}
    assert by_name["Rabies Vaccination"]["count"] == 2
    assert by_name["Rabies Vaccination"]["revenue"] == 5000
    assert by_name["House call"]["revenue"] == 400


def test_dashboard_is_tenant_scoped(client, auth_headers, other_headers):
    other_owner = client.post(
        "/api/v1/owners",
        headers=other_headers,
        json={"name": "Other", "phone": "555-0000"},
    )
    pet = _pet(client, other_headers, other_owner.json(), name="Other Pet")
    service = _service(client, other_headers, "Consultation", 9000)
    visit = client.post(
        "/api/v1/visits",
        headers=other_headers,
        json={
            "pet_id": pet["id"],
            "visit_date": _today().isoformat(),
            "items": [{"service_id": service["id"], "quantity": 1}],
        },
    )
    client.post(
        "/api/v1/payments",
        headers=other_headers,
        json={"visit_id": visit.json()["id"], "amount": 9000, "payment_method": "cash"},
    )
    dashboard = client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    assert dashboard.json()["today"] == {"visits": 0, "revenue": 0}
    assert dashboard.json()["month"]["revenue"] == 0
    assert dashboard.json()["month"]["visits"] == 0
