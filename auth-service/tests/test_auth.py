import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Jane Smith",
            "email": "jane@example.com",
            "password": "securepass123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "jane@example.com"
    assert data["full_name"] == "Jane Smith"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {
        "full_name": "Jane Smith",
        "email": "jane@example.com",
        "password": "securepass123",
    }

    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 400
    assert second.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Jane Smith",
            "email": "jane@example.com",
            "password": "securepass123",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "jane@example.com", "password": "securepass123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Jane Smith",
            "email": "jane@example.com",
            "password": "securepass123",
        },
    )

    wrong_password = await client.post(
        "/api/v1/auth/login",
        json={"email": "jane@example.com", "password": "wrongpassword"},
    )
    assert wrong_password.status_code == 401
    assert wrong_password.json()["detail"] == "Invalid email or password"

    nonexistent_email = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "whatever123"},
    )
    assert nonexistent_email.status_code == 401
    assert nonexistent_email.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_me_endpoint_with_valid_token(client):
    await client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Jane Smith",
            "email": "jane@example.com",
            "password": "securepass123",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "jane@example.com", "password": "securepass123"},
    )
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "jane@example.com"
    assert data["full_name"] == "Jane Smith"


@pytest.mark.asyncio
async def test_me_endpoint_without_token(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_me_endpoint_with_invalid_token(client):
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not.a.real.token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"
