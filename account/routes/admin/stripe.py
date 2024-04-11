"""Billing admin routes."""

from fastapi import APIRouter, Depends, HTTPException

from account.models.user import User
from account.models.util import JustUrl
from account.util.current_user import admin_user, embedded_user
from account.util.stripe import get_portal_session

router = APIRouter(prefix="/stripe")


@router.get("/portal", dependencies=[Depends(admin_user)])
async def get_billing_url(user: User = Depends(embedded_user)) -> JustUrl:
    """Return the Stripe account portal for another user."""
    if not (user.stripe and user.stripe.customer_id):
        raise HTTPException(400, "No stripe fields available")
    session = get_portal_session(user)
    return JustUrl(url=session.url)
