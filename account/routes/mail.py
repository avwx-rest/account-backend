"""
Email router
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Response
from fastapi_jwt_auth.auth_jwt import AuthJWT
from pydantic import EmailStr

from account.models.user import User
from account.util.current_user import current_user
from account.util.mail import send_verification_email
from account.util.mailing import add_to_mailing, remove_from_mailing


router = APIRouter(prefix="/mail", tags=["Mail"])


@router.post("/verify")
async def request_verification_email(
    email: EmailStr = Body(..., embed=True), auth: AuthJWT = Depends()
):
    """Send the user a verification email"""
    user = await User.by_email(email)
    if user.email_confirmed_at is not None:
        raise HTTPException(400, "Email is already verified")
    if user.disabled:
        raise HTTPException(400, "Your account is disabled")
    token = auth.create_access_token(user.email)
    await send_verification_email(email, token)
    return Response(status_code=200)


@router.post("/verify/{token}")
async def verify_email(token: str, auth: AuthJWT = Depends()):
    """Verify the user's email with the supplied token"""
    # Manually assign the token value
    auth._token = token  # pylint: disable=protected-access
    user = await User.by_email(auth.get_jwt_subject())
    if user.email_confirmed_at is not None:
        raise HTTPException(400, "Email is already verified")
    if user.disabled:
        raise HTTPException(400, "Your account is disabled")
    user.email_confirmed_at = datetime.now(tz=timezone.utc)
    await user.save()
    return Response(status_code=200)


@router.post("/list")
async def add_to_mailing_list(user: User = Depends(current_user)):
    """Add the user to the mailing list"""
    if user.subscribed:
        raise HTTPException(400, "User is already subscribed")
    await add_to_mailing(user)
    return Response(status_code=200)


@router.delete("/list")
async def remove_from_mailing_list(user: User = Depends(current_user)):
    """Remove the user from the mailing list"""
    if not user.subscribed:
        raise HTTPException(400, "User is already unsubscribed")
    await remove_from_mailing(user)
    return Response(status_code=204)
