"""
Test data handlers
"""

import asyncio as aio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from account.models.plan import Plan
from account.models.token import TokenUsage
from account.models.user import User, UserToken
from account.util.password import hash_password


DATA = Path(__file__).parent / "data"
PLANS = json.load(DATA.joinpath("plans.json").open())


async def add_empty_user() -> str:
    """Adds minimal user to user collection"""
    email = "empty@test.io"
    user = User(
        email=email,
        password=hash_password(email),
        email_confirmed_at=datetime.now(tz=timezone.utc),
    )
    await user.create()
    return email


async def add_token_user(history: bool = False) -> str:
    """Add user with an app token to user collection"""
    token = await UserToken.new()
    email = "token@test.io"
    now = datetime.now(tz=timezone.utc)
    user = User(
        email=email,
        password=hash_password(email),
        email_confirmed_at=now - timedelta(days=7),
        tokens=[token],
    )
    await user.create()
    if history:
        tasks = []
        for i in range(3):
            day = now - timedelta(days=i)
            usage = TokenUsage(
                token_id=token.id,
                user_id=user.id,
                count=i + 100,
                date=day,
                updated=day,
            )
            tasks.append(usage.create())
        await aio.gather(*tasks)
    return email


async def add_plans(*keys: str) -> None:
    """Add plans by key value"""
    tasks = [Plan(**PLANS[key]).create() for key in keys]
    await aio.gather(*tasks)
