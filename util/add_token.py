"""Create a new API token for a user."""

# stdlib
import sys
import asyncio as aio
from pathlib import Path

# library
import typer
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

# module
from account.config import CONFIG  # noqa: E402
from account.models.plan import Plan  # noqa: E402
from account.models.user import User, UserToken  # noqa: E402


async def main(email: str) -> int:
    """Create a new token for a user."""
    db = AsyncIOMotorClient(CONFIG.mongo_uri).account
    await init_beanie(db, document_models=[Plan, User])  # type: ignore[arg-type]

    user = await User.by_email(email)
    if not user:
        print(f"User with email {email} does not exist")
        return 1

    token = await UserToken.new()
    user.tokens.append(token)
    await user.save()
    print(f"Token created: {token.value}")
    return 0


def add_token(email: str) -> int:
    """Create a new token for a user."""
    return aio.run(main(email))


if __name__ == "__main__":
    typer.run(add_token)
