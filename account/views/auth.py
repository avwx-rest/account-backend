"""
Authentication and registration views
"""

from fastapi import Response

from account.app import app
from account.routers.auth import auth, register, reset_password, verify
from account.util.user_manager import jwt, current_user

TAGS = ["auth"]

app.include_router(auth, prefix="/auth/jwt", tags=TAGS)
app.include_router(register, prefix="/auth", tags=TAGS)
app.include_router(reset_password, prefix="/auth", tags=TAGS)
app.include_router(verify, prefix="/auth", tags=TAGS)


@app.post("/auth/jwt/refresh")
async def refresh_jwt(response: Response, user=current_user):
    return await jwt.get_login_response(user, response)
