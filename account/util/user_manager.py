"""
User and authentication managers
"""

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.db import MongoDBUserDatabase

from account.app import app
from account.config import CONFIG
from account.models.user import User, UserCreate, UserDB, UserUpdate

jwt = JWTAuthentication(
    secret=CONFIG.SECRET_KEY, lifetime_seconds=3600, tokenUrl="/auth/jwt/login"
)

manager = FastAPIUsers(
    MongoDBUserDatabase(UserDB, app.db.userrr),
    [jwt],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

current_user = Depends(manager.get_current_active_user)
