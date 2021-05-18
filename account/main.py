"""
AVWX account management backend
"""

from beanie import init_beanie

from account import views
from account.app import app

from account.models.plan import Plan
from account.models.user import User


@app.on_event("startup")
async def app_init():
    await init_beanie(app.db, document_models=[Plan, User])


# @app.on_event("shutdown")
# async def shutdown_event():
#     app.db.close()
