"""
Stripe callback router
"""

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
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
async def stripe_fulfill(request: Request, stripe_signature: str = Header(None)):
    """Stripe event handler"""
    data = await request.body()
    try:
        event = get_event(data, stripe_signature)
    except (ValueError, SignatureVerificationError) as exc:
        raise HTTPException(400) from exc
    event_type = event["type"]
    if event_type == "checkout.session.completed":
        # Payment is successful and the subscription is created.
        # You should provision the subscription and save the customer ID to your database.
        if await new_subscription(event["data"]["object"]):
            return Response()
    elif event_type == "invoice.paid":
        # Continue to provision the subscription as payments continue to be made.
        # Store the status in your database and check when a user accesses your service.
        # This approach helps you avoid hitting rate limits.
        print(data)
    elif event_type == "invoice.payment_failed":
        # The payment failed or the customer does not have a valid payment method.
        # The subscription becomes past_due. Notify your customer and send them to the
        # customer portal to update their payment information.
        print(data)
    else:
        print(f"Unhandled event type {event_type}")
    raise HTTPException(400)
