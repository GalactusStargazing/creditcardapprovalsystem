import uuid

import pytest

from tests.conftest import make_token

SAMPLE_APPLICATION = {
    "full_name": "Jane Smith",
    "date_of_birth": "1995-06-15",
    "pan_number": "ABCDE1234F",
    "mobile_number": "9876543210",
    "email": "jane@example.com",
    "address": "456 Park Street, Mumbai",
    "occupation": "SALARIED",
    "employer": "Acme Corp",
    "monthly_income": 85000,
    "existing_loan_amount": 5000,
    "credit_score": 750,
    "card_type": "GOLD",
}


@pytest.mark.asyncio
async def test_create_application_success(client):
    user_id = uuid.uuid4()
    token = make_token(user_id)

    response = await client.post(
        "/api/v1/applications",
        json=SAMPLE_APPLICATION,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Jane Smith"
    assert data["card_type"] == "GOLD"
    assert data["status"] == "SUBMITTED"
    assert data["card_number"] is None
    assert "id" in data


@pytest.mark.asyncio
async def test_create_application_without_token(client):
    response = await client.post("/api/v1/applications", json=SAMPLE_APPLICATION)
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_own_applications(client):
    user_id = uuid.uuid4()
    token = make_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}

    await client.post("/api/v1/applications", json=SAMPLE_APPLICATION, headers=headers)
    await client.post("/api/v1/applications", json=SAMPLE_APPLICATION, headers=headers)

    response = await client.get("/api/v1/applications", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all("id" in item and "status" in item for item in data)


@pytest.mark.asyncio
async def test_applications_are_isolated_per_user(client):
    user_a_token = make_token(uuid.uuid4())
    user_b_token = make_token(uuid.uuid4())

    await client.post(
        "/api/v1/applications",
        json=SAMPLE_APPLICATION,
        headers={"Authorization": f"Bearer {user_a_token}"},
    )

    response = await client.get(
        "/api/v1/applications",
        headers={"Authorization": f"Bearer {user_b_token}"},
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_application_detail_success(client):
    user_id = uuid.uuid4()
    token = make_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/api/v1/applications", json=SAMPLE_APPLICATION, headers=headers
    )
    application_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/applications/{application_id}", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == application_id


@pytest.mark.asyncio
async def test_get_application_detail_forbidden_for_other_user(client):
    owner_token = make_token(uuid.uuid4())
    other_user_token = make_token(uuid.uuid4())

    create_response = await client.post(
        "/api/v1/applications",
        json=SAMPLE_APPLICATION,
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    application_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/applications/{application_id}",
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this application"


@pytest.mark.asyncio
async def test_get_application_detail_not_found(client):
    token = make_token(uuid.uuid4())
    fake_id = uuid.uuid4()

    response = await client.get(
        f"/api/v1/applications/{fake_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


@pytest.mark.asyncio
async def test_get_application_status(client):
    token = make_token(uuid.uuid4())
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await client.post(
        "/api/v1/applications", json=SAMPLE_APPLICATION, headers=headers
    )
    application_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/applications/{application_id}/status", headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["application_id"] == application_id
    assert data["status"] == "SUBMITTED"


@pytest.mark.asyncio
async def test_create_application_invalid_credit_score(client):
    token = make_token(uuid.uuid4())
    invalid_data = {**SAMPLE_APPLICATION, "credit_score": 999}

    response = await client.post(
        "/api/v1/applications",
        json=invalid_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_application_invalid_card_type(client):
    token = make_token(uuid.uuid4())
    invalid_data = {**SAMPLE_APPLICATION, "card_type": "DIAMOND"}

    response = await client.post(
        "/api/v1/applications",
        json=invalid_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422
