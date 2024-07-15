"""Populate test token history collection for all users."""

import asyncio as aio

from loader import load_models

from account.models.addon import Addon
from account.models.plan import Plan
from account.models.token import TokenUsage
from account.models.user import User
from tests.data import add_token_usage


async def main() -> None:
    """Populate test token history collection for all users."""
    await load_models(Addon, Plan, TokenUsage, User)

    for user in await User.all().to_list():
        for token in user.tokens:
            await add_token_usage(user, token, days=90)


if __name__ == "__main__":
    aio.run(main())
