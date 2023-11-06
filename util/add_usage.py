"""Populate test token history collection for all users."""

import asyncio as aio

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from account.config import CONFIG
from account.models.addon import Addon
from account.models.plan import Plan
from account.models.token import TokenUsage
from account.models.user import User
from tests.data import add_token_usage


async def main() -> None:
    """Populate test token history collection for all users."""
    db = AsyncIOMotorClient(CONFIG.mongo_uri).account
    await init_beanie(db, document_models=[Addon, Plan, TokenUsage, User])  # type: ignore[arg-type]

    for user in await User.all().to_list():
        for token in user.tokens:
            await add_token_usage(user, token, days=90)


if __name__ == "__main__":
    aio.run(main())
