"""
Token management router
"""

from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT

from account.models.user import Token, TokenOut, User

router = APIRouter(prefix="/token", tags=["Token"])


@router.get("/", response_model=list[TokenOut])
async def get_user_tokens(auth: AuthJWT = Depends()):
    """Returns the current user's tokens"""
    auth.jwt_required()
    user = await User.by_email(auth.get_jwt_subject())
    return user.tokens
