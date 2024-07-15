"""Pytest fixtures."""

from collections.abc import AsyncIterator

import pytest_asyncio
from asgi_lifespan import LifespanManager
from decouple import config
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from account.config import CONFIG

# Override config settings before loading the app
CONFIG.testing = True
CONFIG.mongo_uri = config("TEST_MONGO_URI", default="mongodb://localhost:27017")
CONFIG.database = "account-tests"

from account.main import app  # noqa: E402


async def clear_database(server: FastAPI) -> None:
    """Empty the test database."""
    async for collection in await server.state.db.list_collections():
        await server.state.db[collection["name"]].delete_many({})


@pytest_asyncio.fixture()
async def client() -> AsyncIterator[AsyncClient]:
    """Async server client that handles lifespan and teardown."""
    async with LifespanManager(app):  # noqa SIM117
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as _client:  # type: ignore
            try:
                yield _client
            finally:
                await clear_database(app)
