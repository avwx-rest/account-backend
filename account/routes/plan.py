"""
Plan router
"""

from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT

from account.models.plan import Plan, PlanOut
from account.models.user import User

router = APIRouter(tags=["Plan"])


@router.get("/plans", response_model=list[PlanOut])
async def get_plans():
    """Returns all plans"""
    return await Plan.all().to_list()


@router.get("/plan", response_model=PlanOut)
async def get_user_plan(auth: AuthJWT = Depends()):
    """Returns the current user's plan"""
    auth.jwt_required()
    user = await User.by_email(auth.get_jwt_subject())
    return user.plan
