"""Current user dependency."""

from fastapi import Body, HTTPException, Security
from fastapi_jwt import JwtAuthorizationCredentials

from account.models.user import User
from account.jwt import access_security, user_from_credentials


async def current_user(
    auth: JwtAuthorizationCredentials = Security(access_security),
) -> User:
    """Return the current authorized user."""
    if not auth:
        raise HTTPException(401, "No authorization credentials found")
    user = await user_from_credentials(auth)
    if user is None:
        raise HTTPException(404, "Authorized user could not be found")
    return user


async def embedded_user(email: str = Body(..., embed=True)) -> User:
    """Return a user from an embedded email."""
    if not email:
        raise HTTPException(401, "No user email found")
    user = await User.by_email(email)
    if user is None:
        raise HTTPException(404, "Embedded user could not be found")
    return user


async def admin_user(
    auth: JwtAuthorizationCredentials = Security(access_security),
) -> User:
    """Return the current admin user."""
    user = await current_user(auth)
    if not user.is_admin:
        raise HTTPException(403, "Not allowed to access resource")
    return user
