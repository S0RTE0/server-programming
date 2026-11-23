import pytest
from httpx import AsyncClient


async def test_get_items_empty(client: AsyncClient):
    # Act
    response = await client.get("/items/")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


async def test_item_full_crud(
    client: AsyncClient,
    auth_headers: dict[str, str],
    admin_headers: dict[str, str],
):
    # Arrange
    payload = {"name": "Fire Sword", "item_type": "weapon"}

    # Act: Create
    create_response = await client.post("/items/", json=payload, headers=auth_headers)
    created = create_response.json()

    # Assert: Create
    assert create_response.status_code == 201
    assert created["name"] == payload["name"]
    assert created["item_type"] == payload["item_type"]
    assert "id" in created
    item_id = created["id"]

    # Act & Assert: List and Get by ID
    list_response = await client.get("/items/")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = await client.get(f"/items/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == item_id

    # Act & Assert: Update
    update_response = await client.put(
        f"/items/{item_id}",
        json={"name": "Inferno Sword"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Inferno Sword"
    assert update_response.json()["item_type"] == payload["item_type"]

    # Act & Assert: Delete (admin only)
    delete_response = await client.delete(f"/items/{item_id}", headers=admin_headers)
    assert delete_response.status_code == 204

    # Act & Assert: Not found after delete
    after_delete = await client.get(f"/items/{item_id}")
    assert after_delete.status_code == 404
    assert after_delete.json()["detail"] == "Item not found"


async def test_get_item_not_found(client: AsyncClient):
    # Act
    response = await client.get("/items/9999")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


@pytest.mark.parametrize(
    "invalid_payload",
    [
        {"name": "", "item_type": "weapon"},
        {"name": "Shield", "item_type": ""},
        {"name": "OnlyName"},
        {"item_type": "armor"},
    ],
)
async def test_create_item_validation_error(
    client: AsyncClient,
    auth_headers: dict[str, str],
    invalid_payload: dict,
):
    # Act
    response = await client.post("/items/", json=invalid_payload, headers=auth_headers)

    # Assert
    assert response.status_code == 422


async def test_item_auth_and_rbac(
    client: AsyncClient,
    auth_headers: dict[str, str],
):
    # Arrange
    payload = {"name": "Iron Shield", "item_type": "armor"}

    # Unauthorized POST
    unauth_create = await client.post("/items/", json=payload)
    assert unauth_create.status_code == 401

    # Create as authenticated user
    created = await client.post("/items/", json=payload, headers=auth_headers)
    assert created.status_code == 201
    item_id = created.json()["id"]

    # Unauthorized PUT & DELETE
    assert (
        await client.put(f"/items/{item_id}", json={"name": "X"})
    ).status_code == 401
    assert (await client.delete(f"/items/{item_id}")).status_code == 401

    # Regular user cannot DELETE (403 Forbidden)
    user_delete = await client.delete(f"/items/{item_id}", headers=auth_headers)
    assert user_delete.status_code == 403
