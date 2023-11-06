"""Generate email reset link."""

# stdlib
import sys
from datetime import timedelta
from pathlib import Path

# library
import typer
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
load_dotenv()

# module
from account.jwt import access_security  # noqa: E402


def get_reset_link(email: str) -> int:
    """Generate email reset link."""
    token = access_security.create_access_token(
        {"username": email},
        expires_delta=timedelta(hours=24),
    )
    url = f"https://account.avwx.rest/forgot-password?t={token}"
    print(url)
    return 0


if __name__ == "__main__":
    typer.run(get_reset_link)
