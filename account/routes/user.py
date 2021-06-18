"""
User router
"""

from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT

from account.models.user import User, UserOut

router = APIRouter()


@router.get("/", response_model=UserOut)
async def user(auth: AuthJWT = Depends()):
    """Returns the current user"""
    auth.jwt_required()
    return await User.by_email(auth.get_jwt_subject())
