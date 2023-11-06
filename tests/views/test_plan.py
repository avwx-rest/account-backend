"""Plan information tests."""

import pytest
from httpx import AsyncClient

from tests.data import add_plan_user, add_plans
from tests.util import auth_headers


@pytest.mark.asyncio
async def test_get_plan(client: AsyncClient) -> None:
    """Test plan endpoint returns free plan."""
    key = "free"
    await add_plans(key)
    email = await add_plan_user(key)
    auth = await auth_headers(client, email)
    resp = await client.get("/plan", headers=auth)
    assert resp.status_code == 200
    plan = resp.json()
    assert plan["key"] == key


@pytest.mark.asyncio
async def test_get_all_plans(client: AsyncClient) -> None:
    """Test public plan list endpoint."""
    keys = ("free",)
    await add_plans(*keys)
    resp = await client.get("plan/all")
    assert resp.status_code == 200
    plans = resp.json()
    assert len(plans) == len(keys)
