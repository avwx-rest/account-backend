"""Stripe callback router."""

import rollbar
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from stripe.error import SignatureVerificationError

from account.models.user import User, UserOut
from account.util.current_user import current_user
from account.util.stripe import (
    get_event,
    get_portal_session,
    invoice_failed,
    invoice_paid,
    new_subscription,
)


router = APIRouter(prefix="/stripe", tags=["Stripe"])


@router.get("/success", response_model=UserOut)
async def stripe_success(user: User = Depends(current_user)):  # type: ignore[no-untyped-def]
    """Add success notification after sign-up."""
    await user.add_notification(
        "success", "Your sign-up was successful. Thank you for supporting AVWX!"
    )
    return user


@router.get("/cancel", response_model=UserOut)
async def stripe_cancel(user: User = Depends(current_user)):  # type: ignore[no-untyped-def]
    """Add cancelled notification after sign-up."""
    await user.add_notification(
        "info", "It looks like you cancelled sign-up. No changes have been made"
    )
    return user


_EVENTS = {
    # Payment is successful and the subscription is created.
    # You should provision the subscription and save the customer ID to your database.
    "checkout.session.completed": new_subscription,
    # Continue to provision the subscription as payments continue to be made.
    # Store the status in your database and check when a user accesses your service.
    # This approach helps you avoid hitting rate limits.
    "invoice.paid": invoice_paid,
    # The payment failed or the customer does not have a valid payment method.
    # The subscription becomes past_due. Notify your customer and send them to the
    # customer portal to update their payment information.
    "invoice.payment_failed": invoice_failed,
}


@router.post("/fulfill")
async def stripe_fulfill(
    request: Request, stripe_signature: str = Header(None)
) -> Response:
    """Stripe event handler."""
    data = await request.json()
    try:
        event = get_event(data, stripe_signature)
    except (ValueError, SignatureVerificationError) as exc:
        raise HTTPException(400) from exc
    event_type = event["type"]
    if handler := _EVENTS.get(event_type):
        if await handler(event["data"]["object"]):
            return Response()
    else:
        print(f"Unhandled event type {event_type}")
        rollbar.report_message(event)
    raise HTTPException(400)


@router.get("/portal")
async def customer_portal(user: User = Depends(current_user)) -> dict[str, str] | None:
    """Return the user's Stripe account portal URL."""
    if not user.stripe or user.stripe.customer_id:
        return None
    session = get_portal_session(user)
    return {"url": session.url}
