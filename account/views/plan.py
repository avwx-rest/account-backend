"""
Plan views
"""

from account.app import app
from account.models.plan import Plan
from account.util.user_manager import current_user


@app.get("/plans")
async def plan_list():
    return await Plan.all().to_list()


@app.get("/plan")
async def current_plan(user=current_user):
    """"""
    return user.plan
