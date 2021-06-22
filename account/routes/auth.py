"""
Authentication router
"""

# pylint: disable=too-few-public-methods

from datetime import timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from account.models.user import User, UserAuth
from account.util.password import hash_password


router = APIRouter(prefix="/auth", tags=["Auth"])


class AccessToken(BaseModel):
    """Access token details"""

    access_token: str
    access_token_expires: timedelta = timedelta(minutes=15)


class RefreshToken(AccessToken):
    """Access and refresh token details"""

    refresh_token: str
    refresh_token_expires: timedelta = timedelta(days=30)


@router.post("/login")
async def login(user_auth: UserAuth, auth: AuthJWT = Depends()):
    """Authenticates and returns the user's JWT"""
    user = await User.find_one(User.email == user_auth.email)
    if not user or hash_password(user_auth.password) != user.password:
        raise HTTPException(status_code=401, detail="Bad username or password")
    access_token = auth.create_access_token(subject=user.email)
    refresh_token = auth.create_refresh_token(subject=user.email)
    return RefreshToken(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh(auth: AuthJWT = Depends()):
    """Returns a new access token from a refresh token"""
    auth.jwt_refresh_token_required()
    access_token = auth.create_access_token(subject=auth.get_jwt_subject())
    return AccessToken(access_token=access_token)
