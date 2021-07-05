"""
Authentication tests
"""

import pytest
from httpx import AsyncClient

from tests.data import add_empty_user
from tests.util import auth_headers


@pytest.mark.asyncio
async def test_user_get(client: AsyncClient) -> None:
    """Test user endpoint returns authorized user"""
    await add_empty_user()
    email = "empty@test.io"
    auth = await auth_headers(client, email)
    resp = await client.get("/user", headers=auth)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == email


@pytest.mark.asyncio
async def test_not_authorized(client: AsyncClient) -> None:
    """Test user not authorized if required"""
    resp = await client.get("/user")
    assert resp.status_code == 401
    headers = {"AUTHORIZATION": "Bearer eyJ0eXAiOiJKV1QiLCJhbG"}
    resp = await client.get("/user", headers=headers)
    assert resp.status_code == 422
