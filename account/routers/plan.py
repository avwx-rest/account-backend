"""
Plan routers
"""

from fastapi import APIRouter

from account.models.plan import Plan

router = APIRouter()


@router.get("/")
async def plan_list():
    return await Plan.all().to_list()
