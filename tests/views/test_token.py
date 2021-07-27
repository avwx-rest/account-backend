"""
Token management tests
"""

from datetime import date

import pytest
from httpx import AsyncClient

from tests.data import add_empty_user, add_token_user
from tests.util import auth_headers


def assert_app_token(token: dict, name: str = "Token", active: bool = True) -> None:
    """Checks for default token values"""
    assert token["name"] == name
    assert token["type"] == "app"
    assert type(token["value"]) == str
    assert token["active"] == active


def assert_token_history(history: dict) -> None:
    """Checks token usage fields"""
    assert type(history["count"]) == int
    assert type(history["date"]) == str
    date.fromisoformat(history["date"])


async def assert_token_count(client: AsyncClient, auth: dict, count: int) -> None:
    """Asserts that the user has the expected number of tokens"""
    resp = await client.get("/token", headers=auth)
    assert resp.status_code == 200
    data = resp.json()
    assert type(data) == list
    assert len(data) == count


async def get_token(client: AsyncClient, auth: dict, index: int = 0) -> dict:
    """Returns an existing token"""
    resp = await client.get("/token", headers=auth)
    assert resp.status_code == 200
    return resp.json()[index]


@pytest.mark.asyncio
async def test_get_all_tokens(client: AsyncClient) -> None:
    """Test user endpoint returns authorized user"""
    email = await add_token_user()
    auth = await auth_headers(client, email)
    resp = await client.get("/token", headers=auth)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert_app_token(data[0])


@pytest.mark.asyncio
async def test_new_token(client: AsyncClient) -> None:
    """Test creation of a new user token"""
    email = await add_empty_user()
    auth = await auth_headers(client, email)
    # Check no tokens
    await assert_token_count(client, auth, 0)
    # Add new app token
    resp = await client.post("/token", headers=auth)
    assert resp.status_code == 200
    token = resp.json()
    assert_app_token(token)
    # Check new token
    await assert_token_count(client, auth, 1)


@pytest.mark.asyncio
async def test_get_token(client: AsyncClient) -> None:
    """Test fetching a user token by value"""
    email = await add_token_user()
    auth = await auth_headers(client, email)
    token = await get_token(client, auth)
    # Request token by value
    resp = await client.get("/token/" + token["value"], headers=auth)
    assert resp.status_code == 200
    new_token = resp.json()
    assert_app_token(new_token)
    assert token == new_token


@pytest.mark.asyncio
async def test_update_token(client: AsyncClient) -> None:
    """Test updating fields of a user token"""
    email = await add_token_user()
    auth = await auth_headers(client, email)
    value = (await get_token(client, auth))["value"]
    # Update token name
    name = "New Name"
    resp = await client.patch("/token/" + value, headers=auth, json={"name": name})
    assert resp.status_code == 200
    token = resp.json()
    assert_app_token(token, name=name)
    new_token = await get_token(client, auth)
    assert token == new_token


@pytest.mark.asyncio
async def test_delete_token(client: AsyncClient) -> None:
    """Test deleting a new user token"""
    email = await add_token_user()
    auth = await auth_headers(client, email)
    value = (await get_token(client, auth))["value"]
    # Delete token
    resp = await client.delete("/token/" + value, headers=auth)
    assert resp.status_code == 204
    # Check no tokens
    resp = await client.get("/token/" + value, headers=auth)
    assert resp.status_code == 404
    await assert_token_count(client, auth, 0)


@pytest.mark.asyncio
async def test_token_refresh(client: AsyncClient) -> None:
    """Test refreshing a user token's value"""
    email = await add_token_user()
    auth = await auth_headers(client, email)
    value = (await get_token(client, auth))["value"]
    # Refresh value
    resp = await client.post(f"/token/{value}/refresh", headers=auth)
    assert resp.status_code == 200
    token = resp.json()
    assert_app_token(token)
    new_value = token["value"]
    assert value != new_value
    # Check new value
    resp = await client.get("/token/" + value, headers=auth)
    assert resp.status_code == 404
    resp = await client.get("/token/" + new_value, headers=auth)
    assert resp.status_code == 200
    new_token = resp.json()
    assert_app_token(new_token)
    assert token == new_token


@pytest.mark.asyncio
async def test_token_history(client: AsyncClient) -> None:
    """Test fetching a user's token usage history"""
    email = await add_token_user(history=True)
    auth = await auth_headers(client, email)
    value = (await get_token(client, auth))["value"]
    # Fetch single token history
    resp = await client.get(f"/token/{value}/history", headers=auth)
    assert resp.status_code == 200
    history: list[dict] = resp.json()
    assert len(history) == 3
    for item in history:
        assert_token_history(item)
