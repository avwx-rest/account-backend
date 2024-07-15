"""Verify a user's email."""

import asyncio as aio

import typer
from loader import load_models

from account.models.user import Plan, User


async def main(email: str) -> int:
    """Force validates a user's email."""
    await load_models(User, Plan)
    user = await User.by_email(email)
    if not user:
        print(f"User with email {email} does not exist")
        return 1
    user.validate_email()
    await user.save()
    print(f"{email} has been verified")
    return 0


def validate_email(email: str) -> int:
    """Force validates a user's email."""
    return aio.run(main(email))


if __name__ == "__main__":
    typer.run(validate_email)
