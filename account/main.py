"""
Server main runtime
"""

# pylint: disable=unused-import,import-error

from account import jwt
from account.app import app
from account.routes.auth import router as AuthRouter
from account.routes.mail import router as MailRouter
from account.routes.register import router as RegisterRouter
from account.routes.user import router as UserRouter


app.include_router(AuthRouter, prefix="/auth", tags=["Auth"])
app.include_router(MailRouter, prefix="/mail", tags=["Mail"])
app.include_router(RegisterRouter, prefix="/register", tags=["Register"])
app.include_router(UserRouter, prefix="/user", tags=["User"])
