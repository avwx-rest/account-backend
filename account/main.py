"""
Server main runtime
"""

# pylint: disable=unused-import,import-error

from account import jwt
from account.app import app
from account.routes.auth import router as AuthRouter
from account.routes.mail import router as MailRouter
from account.routes.notification import router as NotificationRouter
from account.routes.plan import router as PlanRouter
from account.routes.register import router as RegisterRouter
from account.routes.stripe import router as StripeRouter
from account.routes.token import router as TokenRouter
from account.routes.user import router as UserRouter


app.include_router(AuthRouter)
app.include_router(MailRouter)
app.include_router(NotificationRouter)
app.include_router(PlanRouter)
app.include_router(RegisterRouter)
app.include_router(StripeRouter)
app.include_router(TokenRouter)
app.include_router(UserRouter)


@app.get("/")
def root():
    return "Hello"
