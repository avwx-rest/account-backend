"""
Account registration tests
"""

import pytest
from httpx import AsyncClient

from account.models.user import User

from tests.data import add_empty_user, add_plans
from tests.util import auth_headers


async def assert_user_count(client: AsyncClient, count: int) -> None:
    """Asserts the number of user documents matches the expected count"""
    assert count == await User.count()


@pytest.mark.asyncio
async def test_new_user(client: AsyncClient) -> None:
    """Test registering a new user"""
    await add_plans("free")
    await assert_user_count(client, 0)
    email, password = "new@test.io", "testing1"
    auth = {"email": email, "password": password, "token": "test"}
    resp = await client.post("/register", json=auth)
    assert resp.status_code == 200
    user = resp.json()
    assert user["email"] == email
    assert "password" not in user
    assert user["plan"]["key"] == "free"
    assert len(user["tokens"]) == 0
    assert len(user["addons"]) == 0
    await assert_user_count(client, 1)
    db_user = await User.by_email(email)
    assert db_user.password != password
    assert db_user.email_confirmed_at is None


@pytest.mark.asyncio
async def test_existing_user(client: AsyncClient) -> None:
    """Test registering an existing user errors"""
    email = await add_empty_user()
    await assert_user_count(client, 1)
    auth = {"email": email, "password": "testing1", "token": "test"}
    resp = await client.post("/register", json=auth)
    assert resp.status_code == 409
    await assert_user_count(client, 1)


@pytest.mark.asyncio
async def test_forgot_password(client: AsyncClient) -> None:
    """Test requesting password reset email"""
    email = await add_empty_user()
    payload = {"email": email}
    resp = await client.post("/register/forgot-password", json=payload)
    assert resp.status_code == 200
    user = await User.by_email(email)
    user.email_confirmed_at = None
    await user.save()
    resp = await client.post("/register/forgot-password", json=payload)
    assert resp.status_code == 400
