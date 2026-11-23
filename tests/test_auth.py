import pytest
from httpx import AsyncClient


async def test_register_success(client: AsyncClient):
    # Arrange
    payload = {
        "email": "newuser@example.com",
        "password": "StrongPassword123",
        "role": "user",
    }

    # Act
    response = await client.post("/register", json=payload)
    data = response.json()

    # Assert
    assert response.status_code == 201
    assert data["email"] == payload["email"]
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "id" in data
    assert "hashed_password" not in data


async def test_register_duplicate_email(client: AsyncClient):
    # Arrange
    payload = {
        "email": "duplicate@example.com",
        "password": "StrongPassword123",
    }
    first_response = await client.post("/register", json=payload)
    assert first_response.status_code == 201

    # Act
    second_response = await client.post("/register", json=payload)

    # Assert
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "User with this email already exists"


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {"email": "not-an-email", "password": "StrongPassword123"},
        {"email": "short@example.com", "password": "123"},
        {
            "email": "badrole@example.com",
            "password": "StrongPassword123",
            "role": "superadmin",
        },
        {"password": "StrongPassword123"},
    ],
)
async def test_register_validation_error(client: AsyncClient, invalid_payload: dict):
    # Act
    response = await client.post("/register", json=invalid_payload)

    # Assert
    assert response.status_code == 422


async def test_login_success(client: AsyncClient):
    # Arrange
    email = "login@example.com"
    password = "LoginPass123"
    await client.post("/register", json={"email": email, "password": password})

    # Act
    response = await client.post(
        "/login",
        data={"username": email, "password": password},
    )
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client: AsyncClient):
    # Arrange
    email = "wrongpass@example.com"
    await client.post("/register", json={"email": email, "password": "CorrectPass123"})

    # Act
    response = await client.post(
        "/login",
        data={"username": email, "password": "WrongPassword"},
    )

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


async def test_login_nonexistent_email(client: AsyncClient):
    # Act
    response = await client.post(
        "/login",
        data={"username": "missing@example.com", "password": "SomePassword123"},
    )

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
