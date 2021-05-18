"""
Plan views
"""

from account.app import app
from account.routers.plan import router

app.include_router(router, prefix="/plans", tags=["plans"])
