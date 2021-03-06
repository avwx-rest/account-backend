"""
Pytest fixtures
"""

# pylint: disable=wrong-import-position

from typing import Iterator

import pytest_asyncio
from asgi_lifespan import LifespanManager
from decouple import config
from fastapi import FastAPI
from httpx import AsyncClient

from account.config import CONFIG


# Override config settings before loading the app
CONFIG.testing = True
CONFIG.mongo_uri = config("TEST_MONGO_URI", default="mongodb://localhost:27017")
CONFIG.database = "account-tests"

from account.main import app


async def clear_database(server: FastAPI) -> None:
    """Empties the test database"""
    for collection in await server.db.list_collections():
        await server.db[collection["name"]].delete_many({})


@pytest_asyncio.fixture()
async def client() -> Iterator[AsyncClient]:
    """Async server client that handles lifespan and teardown"""
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as _client:
            try:
                yield _client
            except Exception as exc:  # pylint: disable=broad-except
                print(exc)
            finally:
                await clear_database(app)
