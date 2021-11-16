"""
Authentication router
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from account.models.auth import (
    AccessToken,
    RefreshToken,
    ACCESS_EXPIRES,
    REFRESH_EXPIRES,
)
from account.models.user import User, UserAuth
from account.util.password import hash_password


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(user_auth: UserAuth, auth: AuthJWT = Depends()):
    """Authenticates and returns the user's JWT"""
    user = await User.by_email(user_auth.email)
    if user is None or hash_password(user_auth.password) != user.password:
        raise HTTPException(status_code=401, detail="Bad email or password")
    if user.email_confirmed_at is None:
        raise HTTPException(status_code=400, detail="Email is not yet verified")
    access_token = auth.create_access_token(
        subject=user.email, expires_time=ACCESS_EXPIRES
    )
    refresh_token = auth.create_refresh_token(
        subject=user.email, expires_time=REFRESH_EXPIRES
    )
    return RefreshToken(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh(auth: AuthJWT = Depends()):
    """Returns a new access token from a refresh token"""
    auth.jwt_refresh_token_required()
    access_token = auth.create_access_token(subject=auth.get_jwt_subject())
    return AccessToken(access_token=access_token)
