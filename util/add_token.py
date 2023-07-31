"""
Create a new API token for a user
"""

# stdlib
import sys
import asyncio as aio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

# library
import typer
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

# module
from account.config import CONFIG
from account.models.plan import Plan
from account.models.user import User, UserToken


async def main(email: str) -> int:
    db = AsyncIOMotorClient(CONFIG.mongo_uri).account
    await init_beanie(db, document_models=[Plan, User])

    user = await User.by_email(email)
    if not user:
        print(f"User with email {email} does not exist")
        return 1

    token = await UserToken.new()
    user.tokens.append(token)
    await user.save()
    print(f"Token created: {token.value}")
    return 0


def add_token(email) -> int:
    """Create a new token for a user"""
    aio.run(main(email))


if __name__ == "__main__":
    typer.run(add_token)
