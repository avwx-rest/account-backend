"""Create a new API token for a user."""

import asyncio as aio

import typer
from loader import load_models

from account.models.user import Plan, User, UserToken


async def main(email: str) -> int:
    """Create a new token for a user."""
    await load_models(Plan, User)

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
