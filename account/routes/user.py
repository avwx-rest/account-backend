"""User router."""

from fastapi import APIRouter, Depends, HTTPException, Response, Security
from fastapi_jwt import JwtAuthorizationCredentials

from account.jwt import access_security
from account.models.user import User, UserOut, UserUpdate
from account.util.current_user import current_user
from account.util.mail import send_email_change
from account.util.mailing import update_mailing
from account.util.stripe import update_email as update_stripe_email

router = APIRouter(prefix="/user", tags=["User"])


@router.get("", response_model=UserOut)
async def get_user(user: User = Depends(current_user)) -> User:
    """Return the current user."""
    return user


@router.patch("", response_model=UserOut)
async def update_user(update: UserUpdate, user: User = Depends(current_user)) -> User:
    """Update allowed user fields."""
    fields = update.model_dump(exclude_unset=True)
    new_email = fields.pop("email", None)
    if new_email and new_email != user.email:
        if await User.by_email(new_email) is not None:
            raise HTTPException(400, "Email already exists")
        if user.subscribed:
            await update_mailing(user.email, new_email)
        update_stripe_email(user, new_email)
        await send_email_change(user.email, new_email)
        user.update_email(new_email)
    user = user.model_copy(update=fields)
    await user.save()
    return user


@router.delete("")
async def delete_user(
    auth: JwtAuthorizationCredentials = Security(access_security),
) -> Response:
    """Delete current user."""
    await User.find_one(User.email == auth.subject["username"]).delete()
    return Response(status_code=204)
