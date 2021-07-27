"""
Test data handlers
"""

import asyncio as aio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from account.models.plan import Plan
from account.models.token import TokenUsage
from account.models.user import User, UserToken
from account.util.password import hash_password


DATA = Path(__file__).parent / "data"
PLANS = json.load(DATA.joinpath("plans.json").open())


def make_user(email: str, offset: Optional[int] = 0) -> User:
    """Returns a minimal, uncommitted User"""
    now = None
    if offset is not None:
        now = datetime.now(tz=timezone.utc) - timedelta(days=offset)
    user = User(
        email=email,
        password=hash_password(email),
        email_confirmed_at=now,
    )
    return user


async def add_empty_user() -> str:
    """Adds minimal user to user collection"""
    user = make_user("empty@test.io")
    await user.create()
    return user.email


async def add_token_user(history: bool = False) -> str:
    """Add user with an app token to user collection"""
    user = make_user("token@test.io", offset=7)
    token = await UserToken.new()
    user.tokens = [token]
    await user.create()
    if history:
        now = datetime.now(tz=timezone.utc)
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
    return user.email


async def add_plan_user(plan: str = "free") -> str:
    """Add user with a specific plan to user collection"""
    user = make_user(f"plan-{plan}@test.io")
    user.plan = await Plan.by_key(plan)
    await user.create()
    return user.email


async def add_plans(*keys: str) -> None:
    """Add plans by key value"""
    tasks = [Plan(**PLANS[key]).create() for key in keys]
    await aio.gather(*tasks)
