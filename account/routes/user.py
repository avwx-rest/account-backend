"""
User router
"""

from fastapi import APIRouter, Depends, Response
from fastapi_jwt_auth import AuthJWT

from account.models.user import User, UserOut, UserUpdate

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/", response_model=UserOut)
async def get_user(auth: AuthJWT = Depends()):
    """Returns the current user"""
    auth.jwt_required()
    return await User.by_email(auth.get_jwt_subject())


@router.patch("/", response_model=UserOut)
async def update_user(update: UserUpdate, auth: AuthJWT = Depends()):
    """Update allowed user fields"""
    auth.jwt_required()
    user = await User.by_email(auth.get_jwt_subject())
    user = user.copy(update=update.dict(exclude_unset=True))
    await user.save()
    return user


@router.delete("/")
async def delete_user(auth: AuthJWT = Depends()):
    """Delete current user"""
    auth.jwt_required()
    await User.find_one(User.email == auth.get_jwt_subject()).delete()
    return Response(status_code=204)
