"""User data admin routes."""

from fastapi import APIRouter, Depends, Response

from account.models.user import User, UserOut
from account.util.current_user import admin_user, embedded_user

router = APIRouter(prefix="/user")


@router.post("/data", dependencies=[Depends(admin_user)])
async def get_user_data(user: User = Depends(embedded_user)) -> UserOut:
    """Return basic information for another user."""
    return user


@router.post("/validate", dependencies=[Depends(admin_user)])
async def validate_user_email(user: User = Depends(embedded_user)) -> Response:
    """Validate the email of another user."""
    user.validate_email()
    await user.save()
    return Response(status_code=200)
