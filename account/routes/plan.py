"""
Plan router
"""

from fastapi import APIRouter, Body, Depends, HTTPException

from account.models.plan import Plan, PlanOut
from account.models.user import User
from account.util.current_user import current_user
from account.util.stripe import get_session, change_subscription, cancel_subscription

router = APIRouter(tags=["Plan"])


@router.get("/plan", response_model=PlanOut)
async def get_user_plan(user: User = Depends(current_user)):
    """Returns the current user's plan"""
    return user.plan


@router.post("/plan")
async def change_plan(key: Body(..., embed=True), user: User = Depends(current_user)):
    """Change the user's current plan. Returns Stripe session if Checkout is required"""
    plan = await Plan.by_key(key)
    if plan is None:
        raise HTTPException(404, f"Plan with key {key} does not exist")
    if user.plan.key == plan.key:
        raise HTTPException(400, f"User is already subscribed to the {plan.name} plan")
    msg = f"Your {plan.name} plan is now active"
    if plan.stripe_id:
        if user.stripe is None or not user.stripe.customer_id is None:
            return get_session(user, plan)
        if not change_subscription(user, plan):
            await user.add_notification("error", "Unable to update your subscription")
            return
        msg += ". Thank you for supporting AVWX!"
    else:
        cancel_subscription(user)
    await user.add_notification("success", msg)


@router.get("/plan/all", response_model=list[PlanOut])
async def get_plans():
    """Returns all plans"""
    return await Plan.all().to_list()
