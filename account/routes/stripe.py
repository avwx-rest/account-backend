"""
Stripe callback router
"""

import rollbar
from fastapi import APIRouter, Body, Depends, Header, HTTPException, Response
from stripe.error import SignatureVerificationError

from account.models.user import User, UserOut
from account.util.current_user import current_user
from account.util.stripe import get_event, new_subscription


router = APIRouter(prefix="/stripe", tags=["Stripe"])


@router.get("/success", response_model=UserOut)
async def stripe_success(user: User = Depends(current_user)):
    """Adds success notification after sign-up"""
    await user.add_notification(
        "success", "Your sign-up was successful. Thank you for supporting AVWX!"
    )
    return user


@router.get("/cancel", response_model=UserOut)
async def stripe_cancel(user: User = Depends(current_user)):
    """Adds cancelled notification after sign-up"""
    await user.add_notification(
        "info", "It looks like you cancelled sign-up. No changes have been made"
    )
    return user


@router.post("/fulfill")
async def stripe_fulfill(stripe_signature: str = Header(None), data: dict = Body(...)):
    """Stripe event handler"""
    # print(data)
    try:
        event = get_event(data, stripe_signature)
    except (ValueError, SignatureVerificationError) as exc:
        raise HTTPException(400) from exc
    # print(event)
    rollbar.report_message("checkout instance", extra_data=data)
    if event["type"] == "checkout.session.completed":
        if new_subscription(event["data"]["object"]):
            return Response()
    raise HTTPException(400)
