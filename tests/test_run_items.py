import uuid

import pytest
from httpx import AsyncClient


async def test_get_run_items_empty(client: AsyncClient):
    # Act
    response = await client.get("/run-items/")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


async def test_run_item_full_crud(
    client: AsyncClient,
    auth_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    # Arrange: create player, game_run, and item
    player = (
        await client.post(
            "/players/",
            json={"username": "collector", "email": "collector@example.com"},
            headers=auth_headers,
        )
    ).json()
    game_run = (
        await client.post(
            "/game-runs/",
            json={"player_id": player["id"], "score": 500},
            headers=auth_headers,
        )
    ).json()
    item = (
        await client.post(
            "/items/",
            json={"name": "Health Potion", "item_type": "consumable"},
            headers=auth_headers,
        )
    ).json()

    run_id = game_run["id"]
    item_id = item["id"]
    payload = {"run_id": run_id, "item_id": item_id, "level": 1}

    # Act: Create
    create_response = await client.post(
        "/run-items/", json=payload, headers=auth_headers
    )
    created = create_response.json()

    # Assert: Create
    assert create_response.status_code == 201
    assert created["run_id"] == run_id
    assert created["item_id"] == item_id
    assert created["level"] == 1

    # Act & Assert: List and Get by composite ID
    list_response = await client.get("/run-items/")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = await client.get(f"/run-items/{run_id}/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["level"] == 1

    # Act & Assert: Update
    update_response = await client.put(
        f"/run-items/{run_id}/{item_id}",
        json={"level": 5},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["level"] == 5

    # Act & Assert: Delete (admin only)
    delete_response = await client.delete(
        f"/run-items/{run_id}/{item_id}",
        headers=admin_headers,
    )
    assert delete_response.status_code == 204

    # Act & Assert: Not found after delete
    after_delete = await client.get(f"/run-items/{run_id}/{item_id}")
    assert after_delete.status_code == 404
    assert after_delete.json()["detail"] == "RunItem not found"


async def test_get_run_item_not_found(client: AsyncClient):
    # Act
    response = await client.get(f"/run-items/{uuid.uuid4()}/999")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "RunItem not found"


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {"run_id": "bad-uuid", "item_id": 1, "level": 1},
        {"run_id": str(uuid.uuid4()), "item_id": 0, "level": 1},
        {"run_id": str(uuid.uuid4()), "item_id": 1, "level": 0},
        {"item_id": 1, "level": 1},
    ],
)
async def test_create_run_item_validation_error(
    client: AsyncClient,
    auth_headers: dict[str, str],
    invalid_payload: dict,
):
    # Act
    response = await client.post(
        "/run-items/", json=invalid_payload, headers=auth_headers
    )

    # Assert
    assert response.status_code == 422


async def test_run_item_auth_and_rbac(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    # Arrange
    player = (
        await client.post(
            "/players/",
            json={"username": "rbac_col", "email": "rbac_col@example.com"},
            headers=auth_headers,
        )
    ).json()
    game_run = (
        await client.post(
            "/game-runs/",
            json={"player_id": player["id"]},
            headers=auth_headers,
        )
    ).json()
    item = (
        await client.post(
            "/items/",
            json={"name": "Mana Ring", "item_type": "accessory"},
            headers=auth_headers,
        )
    ).json()

    run_id = game_run["id"]
    item_id = item["id"]
    payload = {"run_id": run_id, "item_id": item_id, "level": 2}

    # Unauthorized POST
    assert (await client.post("/run-items/", json=payload)).status_code == 401

    # Create as authenticated user
    created = await client.post("/run-items/", json=payload, headers=auth_headers)
    assert created.status_code == 201

    # Unauthorized PUT & DELETE
    assert (
        await client.put(f"/run-items/{run_id}/{item_id}", json={"level": 3})
    ).status_code == 401
    assert (await client.delete(f"/run-items/{run_id}/{item_id}")).status_code == 401

    # Regular user cannot DELETE (403 Forbidden)
    user_delete = await client.delete(
        f"/run-items/{run_id}/{item_id}", headers=auth_headers
    )
    assert user_delete.status_code == 403
