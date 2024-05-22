"""Email router."""

from fastapi import APIRouter, Body, Depends, HTTPException, Response
from pydantic import EmailStr

from account.models.user import User
from account.jwt import access_security, user_from_token
from account.util.current_user import current_user
from account.util.mail import send_verification_email
from account.util.mailing import add_to_mailing, remove_from_mailing


router = APIRouter(prefix="/mail", tags=["Mail"])


@router.post("/verify")
async def request_verification_email(
    email: EmailStr = Body(..., embed=True),
) -> Response:
    """Send the user a verification email."""
    user = await User.by_email(email)
    if user is None:
        raise HTTPException(404, "No user found with that email")
    if user.email_confirmed_at is not None:
        raise HTTPException(400, "Email is already verified")
    if user.disabled:
        raise HTTPException(400, "Your account is disabled")
    token = access_security.create_access_token(user.jwt_subject)
    await send_verification_email(email, token)
    return Response(status_code=200)


@router.post("/verify/{token}")
async def verify_email(token: str) -> Response:
    """Verify the user's email with the supplied token."""
    user = await user_from_token(token)
    if user is None:
        raise HTTPException(404, "No user found with that email")
    user.validate_email()
    await user.save()
    return Response(status_code=200)


@router.post("/list")
async def add_to_mailing_list(user: User = Depends(current_user)) -> Response:
    """Add the user to the mailing list."""
    if user.subscribed:
        raise HTTPException(400, "User is already subscribed")
    await add_to_mailing(user)
    await user.save()
    return Response(status_code=200)


@router.delete("/list")
async def remove_from_mailing_list(user: User = Depends(current_user)) -> Response:
    """Remove the user from the mailing list."""
    if not user.subscribed:
        raise HTTPException(400, "User is already unsubscribed")
    await remove_from_mailing(user)
    await user.save()
    return Response(status_code=204)
