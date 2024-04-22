"""User data admin routes."""

from fastapi import APIRouter, Depends

from account.models.user import User, UserOut
from account.util.current_user import admin_user, embedded_user

router = APIRouter(prefix="/user")


@router.post("/data", dependencies=[Depends(admin_user)])
async def get_user_data(user: User = Depends(embedded_user)) -> UserOut:
    """Return basic information for another user."""
    return user
