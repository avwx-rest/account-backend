"""
Auth response models
"""

# pylint: disable=too-few-public-methods

from datetime import timedelta

from pydantic import BaseModel


ACCESS_EXPIRES = timedelta(minutes=15)
REFRESH_EXPIRES = timedelta(days=30)


class AccessToken(BaseModel):
    """Access token details"""

    access_token: str
    access_token_expires: timedelta = ACCESS_EXPIRES


class RefreshToken(AccessToken):
    """Access and refresh token details"""

    refresh_token: str
    refresh_token_expires: timedelta = REFRESH_EXPIRES
