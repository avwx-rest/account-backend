"""
Authentication router
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi_jwt_auth import AuthJWT

from account.models.user import User, UserAuth
from account.util.password import hash_password


router = APIRouter()


@router.post("/login")
async def login(user_auth: UserAuth, auth: AuthJWT = Depends()):
    """Authenticates and returns the user's JWT"""
    user = await User.find_one(User.email == user_auth.email)
    if not user or hash_password(user_auth.password) != user.password:
        raise HTTPException(status_code=401, detail="Bad username or password")
    access_token = auth.create_access_token(subject=user.email)
    return {"access_token": access_token}
