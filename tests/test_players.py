import uuid

import pytest
from httpx import AsyncClient


async def test_get_players_empty(client: AsyncClient):
    # Act
    response = await client.get("/players/")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


async def test_player_full_crud(
    client: AsyncClient,
    auth_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    # Arrange
    payload = {
        "username": "hero_one",
        "email": "hero@example.com",
        "total_coins": 150,
    }

    # Act: Create
    create_response = await client.post("/players/", json=payload, headers=auth_headers)
    created = create_response.json()

    # Assert: Create
    assert create_response.status_code == 201
    assert created["username"] == payload["username"]
    assert created["email"] == payload["email"]
    assert created["total_coins"] == payload["total_coins"]
    assert "id" in created
    player_id = created["id"]

    # Act & Assert: List and Get by ID
    list_response = await client.get("/players/")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = await client.get(f"/players/{player_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == player_id

    # Act & Assert: Update
    update_response = await client.put(
        f"/players/{player_id}",
        json={"total_coins": 500},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["total_coins"] == 500
    assert update_response.json()["username"] == payload["username"]

    # Act & Assert: Delete (admin only)
    delete_response = await client.delete(
        f"/players/{player_id}",
        headers=admin_headers,
    )
    assert delete_response.status_code == 204

    # Act & Assert: Not found after delete
    after_delete = await client.get(f"/players/{player_id}")
    assert after_delete.status_code == 404
    assert after_delete.json()["detail"] == "Player not found"


async def test_get_player_not_found(client: AsyncClient):
    # Act
    response = await client.get(f"/players/{uuid.uuid4()}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Player not found"


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {"username": "", "email": "a@example.com", "total_coins": 10},
        {"username": "player1", "email": "invalid-email", "total_coins": 10},
        {"username": "player1", "email": "a@example.com", "total_coins": -5},
        {"email": "a@example.com"},
    ],
)
async def test_create_player_validation_error(
    client: AsyncClient,
    auth_headers: dict[str, str],
    invalid_payload: dict,
):
    # Act
    response = await client.post(
        "/players/", json=invalid_payload, headers=auth_headers
    )

    # Assert
    assert response.status_code == 422


async def test_player_auth_and_rbac(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    # Arrange
    payload = {"username": "rbac_player", "email": "rbac@example.com"}

    # Act & Assert: Unauthorized POST
    unauth_create = await client.post("/players/", json=payload)
    assert unauth_create.status_code == 401

    # Create as authenticated user
    created = await client.post("/players/", json=payload, headers=auth_headers)
    assert created.status_code == 201
    player_id = created.json()["id"]

    # Act & Assert: Unauthorized PUT and DELETE
    unauth_update = await client.put(f"/players/{player_id}", json={"total_coins": 10})
    assert unauth_update.status_code == 401

    unauth_delete = await client.delete(f"/players/{player_id}")
    assert unauth_delete.status_code == 401

    # Act & Assert: Regular user cannot DELETE (403 Forbidden)
    user_delete = await client.delete(f"/players/{player_id}", headers=auth_headers)
    assert user_delete.status_code == 403
