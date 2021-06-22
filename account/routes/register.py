"""
Registration router
"""

from fastapi import APIRouter, HTTPException

from account.models.user import User, UserAuth, UserOut
from account.util.password import hash_password

router = APIRouter(prefix="/register", tags=["Register"])


@router.post("/", response_model=UserOut)
async def user_registration(user_auth: UserAuth):
    """Creates a new user"""
    user = await User.by_email(user_auth.email)
    if user is not None:
        raise HTTPException(409, "User with that email already exists")
    hashed = hash_password(user_auth.password)
    user = User(email=user_auth.email, password=hashed)
    await user.add_default_documents()
    await user.create()
    return user
