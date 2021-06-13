"""
JWT authentication and registration routers
"""

from fastapi import Request

from account.config import CONFIG
from account.models.user import UserDB
from account.util.user_manager import jwt, manager


async def on_after_register(user: UserDB, request: Request):
    """Complete UserDB creation"""
    # Pull from DB with filled id field. Email is unique
    new_user = await user.find_one({UserDB.email: user.email})
    await new_user.set_new_user_defaults()
    user.plan, user.tokens = new_user.plan, new_user.tokens
    print(f"User {user.id} has registered.")


def on_after_forgot_password(user: UserDB, token: str, request: Request):
    print(f"User {user.id} has forgot their password. Reset token: {token}")


def after_verification_request(user: UserDB, token: str, request: Request):

    # This is where you send the verification email

    print(f"Verification requested for user {user.id}. Verification token: {token}")


auth = manager.get_auth_router(jwt)
register = manager.get_register_router(on_after_register)
reset_password = manager.get_reset_password_router(
    CONFIG.SECRET_KEY, after_forgot_password=on_after_forgot_password
)
verify = manager.get_verify_router(
    CONFIG.SECRET_KEY, after_verification_request=after_verification_request
)
