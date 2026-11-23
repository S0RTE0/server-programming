import uuid

import pytest
from httpx import AsyncClient


async def test_get_game_runs_empty(client: AsyncClient):
    # Act
    response = await client.get("/game-runs/")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


async def test_game_run_full_crud(
    client: AsyncClient,
    auth_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    # Arrange: create player first
    player_response = await client.post(
        "/players/",
        json={"username": "runner", "email": "runner@example.com"},
        headers=auth_headers,
    )
    player_id = player_response.json()["id"]

    payload = {
        "player_id": player_id,
        "score": 1200,
        "waves_cleared": 5,
        "survival_time_sec": 300,
    }

    # Act: Create
    create_response = await client.post(
        "/game-runs/", json=payload, headers=auth_headers
    )
    created = create_response.json()

    # Assert: Create
    assert create_response.status_code == 201
    assert created["player_id"] == player_id
    assert created["score"] == 1200
    assert created["waves_cleared"] == 5
    assert created["survival_time_sec"] == 300
    run_id = created["id"]

    # Act & Assert: List and Get by ID
    list_response = await client.get("/game-runs/")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = await client.get(f"/game-runs/{run_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == run_id

    # Act & Assert: Update
    update_response = await client.put(
        f"/game-runs/{run_id}",
        json={"score": 2500, "waves_cleared": 10},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["score"] == 2500
    assert update_response.json()["waves_cleared"] == 10

    # Act & Assert: Delete (admin only)
    delete_response = await client.delete(f"/game-runs/{run_id}", headers=admin_headers)
    assert delete_response.status_code == 204

    # Act & Assert: Not found after delete
    after_delete = await client.get(f"/game-runs/{run_id}")
    assert after_delete.status_code == 404
    assert after_delete.json()["detail"] == "GameRun not found"


async def test_get_game_run_not_found(client: AsyncClient):
    # Act
    response = await client.get(f"/game-runs/{uuid.uuid4()}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "GameRun not found"


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {"player_id": "not-a-uuid", "score": 100},
        {"player_id": str(uuid.uuid4()), "score": -10},
        {"player_id": str(uuid.uuid4()), "waves_cleared": -1},
        {"player_id": str(uuid.uuid4()), "survival_time_sec": -5},
        {"score": 100},
    ],
)
async def test_create_game_run_validation_error(
    client: AsyncClient,
    auth_headers: dict[str, str],
    invalid_payload: dict,
):
    # Act
    response = await client.post(
        "/game-runs/", json=invalid_payload, headers=auth_headers
    )

    # Assert
    assert response.status_code == 422


async def test_game_run_auth_and_rbac(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    # Arrange
    player_response = await client.post(
        "/players/",
        json={"username": "rbac_runner", "email": "rbac_runner@example.com"},
        headers=auth_headers,
    )
    player_id = player_response.json()["id"]
    payload = {"player_id": player_id, "score": 300}

    # Unauthorized POST
    assert (await client.post("/game-runs/", json=payload)).status_code == 401

    # Create as authenticated user
    created = await client.post("/game-runs/", json=payload, headers=auth_headers)
    assert created.status_code == 201
    run_id = created.json()["id"]

    # Unauthorized PUT & DELETE
    assert (
        await client.put(f"/game-runs/{run_id}", json={"score": 400})
    ).status_code == 401
    assert (await client.delete(f"/game-runs/{run_id}")).status_code == 401

    # Regular user cannot DELETE (403 Forbidden)
    user_delete = await client.delete(f"/game-runs/{run_id}", headers=auth_headers)
    assert user_delete.status_code == 403
