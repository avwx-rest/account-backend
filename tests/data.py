"""Test data handlers."""

import asyncio as aio
import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

from account.models.plan import Plan
from account.models.token import TokenUsage
from account.models.user import Notification, User, UserToken
from account.util.password import hash_password

DATA = Path(__file__).parent / "data"
PLANS = json.load(DATA.joinpath("plans.json").open())


def make_user(email: str, offset: int | None = 0) -> User:
    """Return a minimal, uncommitted User."""
    now = None if offset is None else datetime.now(tz=UTC) - timedelta(days=offset)
    return User(
        email=email,
        password=hash_password(email),
        email_confirmed_at=now,
    )


async def add_token_usage(user: User, token: UserToken, days: int = 30) -> None:
    """Add historic token usage for a user."""
    assert user.id is not None
    value = random.randint(0, 3000)
    today = datetime.now(tz=UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    tasks = []
    for i in range(-days + 1, 1):
        if not value:
            continue
        date = today + timedelta(days=i)
        usage = TokenUsage(
            token_id=token.id,  # type: ignore[arg-type]
            user_id=user.id,
            count=value,
            date=date,
            updated=date,
        )
        tasks.append(usage.create())
        value += random.randint(-100, 100)
        value = max(value, 0)
    await aio.gather(*tasks)


async def add_empty_user() -> str:
    """Add minimal user to user collection."""
    user = make_user("empty@test.io")
    await user.create()
    return user.email


async def add_token_user(*, history: bool = False) -> str:
    """Add user with an app token to user collection."""
    user = make_user("token@test.io", offset=7)
    token = await UserToken.new()
    user.tokens = [token]
    await user.create()
    if history:
        await add_token_usage(user, token, days=3)
    return user.email


async def add_plan_user(plan: str = "free") -> str:
    """Add user with a specific plan to user collection."""
    user = make_user(f"plan-{plan}@test.io")
    user.plan = await Plan.by_key(plan)
    await user.create()
    return user.email


async def add_notification_user(*text: str) -> str:
    """Add user with notifications to user collection."""
    user = make_user("notification@test.io")
    user.notifications = [Notification(type="app", text=t) for t in text]
    await user.create()
    return user.email


async def add_plans(*keys: str) -> None:
    """Add plans by key value."""
    tasks = [Plan(**PLANS[key]).create() for key in keys]
    await aio.gather(*tasks)
