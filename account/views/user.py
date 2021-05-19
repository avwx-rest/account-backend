"""
User views
"""

from account.app import app
from account.routers.user import current_user

app.include_router(current_user, tags=["user"])
