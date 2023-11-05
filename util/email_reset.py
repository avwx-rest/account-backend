"""
Generate email reset link
"""

# stdlib
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

# library
import typer
from dotenv import load_dotenv

# module
from account.jwt import access_security

load_dotenv()


def get_reset_link(email: str):
    token = access_security.create_access_token(
        {"username": email},
        expires_delta=timedelta(hours=24),
    )
    url = f"https://account.avwx.rest/forgot-password?t={token}"
    print(url)


if __name__ == "__main__":
    typer.run(get_reset_link)
