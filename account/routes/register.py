"""
Registration router
"""

from fastapi import APIRouter, Body, Depends, HTTPException, Response
from fastapi_jwt_auth import AuthJWT
from pydantic import EmailStr

from account.models.user import User, UserRegister, UserOut
from account.util.mail import send_password_reset_email
from account.util.password import hash_password
from account.util.recaptcha import verify

router = APIRouter(prefix="/register", tags=["Register"])

embed = Body(..., embed=True)


@router.post("", response_model=UserOut)
async def user_registration(user_auth: UserRegister):
    """Creates a new user"""
    user = await User.by_email(user_auth.email)
    if user is not None:
        raise HTTPException(409, "User with that email already exists")
    if not await verify(user_auth.token):
        raise HTTPException(407, "It doesn't look like you're a human")
    hashed = hash_password(user_auth.password)
    user = User(email=user_auth.email, password=hashed)
    await user.add_default_documents()
    await user.create()
    return user


@router.post("/forgot-password")
async def forgot_password(email: EmailStr = embed, auth: AuthJWT = Depends()):
    """Sends password reset email"""
    user = await User.by_email(email)
    if user is None:
        raise HTTPException(404, "No user found with that email")
    if user.email_confirmed_at is None:
        raise HTTPException(400, "Email is not yet verified")
    if user.disabled:
        raise HTTPException(400, "Your account is disabled")
    token = auth.create_access_token(user.email)
    await send_password_reset_email(email, token)
    return Response(status_code=200)


@router.post("/reset-password/{token}", response_model=UserOut)
async def reset_password(token: str, password: str = embed, auth: AuthJWT = Depends()):
    """Reset user password from token value"""
    # Manually assign the token value
    auth._token = token  # pylint: disable=protected-access
    user = await User.by_email(auth.get_jwt_subject())
    if user is None:
        raise HTTPException(404, "No user found with that email")
    if user.email_confirmed_at is None:
        raise HTTPException(400, "Email is not yet verified")
    if user.disabled:
        raise HTTPException(400, "Your account is disabled")
    user.password = hash_password(password)
    await user.save()
    return user
