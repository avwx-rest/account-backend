"""
Test data handlers
"""

from datetime import datetime, timezone

from account.models.user import User, UserToken
from account.util.password import hash_password


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


async def add_token_user() -> str:
    """Add user with an app token to user collection"""
    token = await UserToken.new()
    email = "token@test.io"
    user = User(
        email=email,
        password=hash_password(email),
        email_confirmed_at=datetime.now(tz=timezone.utc),
        tokens=[token],
    )
    await user.create()
    return email
