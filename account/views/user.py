"""
User views
"""

from account.app import app
from account.routers.user import user

app.include_router(user, prefix="/users", tags=["users"])
