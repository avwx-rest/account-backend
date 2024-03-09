"""Password utility functions."""

import bcrypt

from account.config import CONFIG


def hash_password(password: str) -> str:
    """Return a salted password hash."""
    return bcrypt.hashpw(password.encode(), CONFIG.salt).decode()


# def verify_and_update(original: str, password: str) -> Tuple[bool, str]:
#     """Verify the original password and returns a new hash."""
#     return _pass_context.verify_and_update(original, CONFIG.SALT + password)
