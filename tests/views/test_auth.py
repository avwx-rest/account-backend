"""
"""

import pytest
from httpx import AsyncClient

from tests.setup import get_test_app

app = get_test_app()

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        data = {"username": "test1", "password": "testing1"}
        response = await ac.post("/login", data=data)
    assert response.status_code == 200
    assert response.json() == {"": None}
