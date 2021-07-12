"""
Plan router
"""

from fastapi import APIRouter, Depends

from account.models.plan import Plan, PlanOut
from account.models.user import User
from account.util.current_user import current_user

router = APIRouter(tags=["Plan"])


@router.get("/plan", response_model=PlanOut)
async def get_user_plan(user: User = Depends(current_user)):
    """Returns the current user's plan"""
    return user.plan


@router.get("/plan/all", response_model=list[PlanOut])
async def get_plans():
    """Returns all plans"""
    return await Plan.all().to_list()
