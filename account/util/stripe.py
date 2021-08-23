"""
Stripe subscription utilities
"""

import stripe
from stripe import Event, Subscription, Webhook
from bson.objectid import ObjectId

from account.config import CONFIG
from account.models.plan import Plan
from account.models.user import Stripe, User


stripe.api_key = CONFIG.stripe_secret_key

_SESSION = {
    "payment_method_types": ["card"],
    "success_url": CONFIG.root_url + "/stripe/success",
    "cancel_url": CONFIG.root_url + "/stripe/cancel",
}


def get_session(user: User, plan: Plan) -> stripe.checkout.Session:
    """Creates a Stripe Session object to start a Checkout"""
    params = {
        "client_reference_id": user.id,
        "subscription_data": {"items": [{"plan": plan.stripe_id}]},
        **_SESSION,
    }
    if user.stripe:
        params["customer"] = user.stripe.customer_id
    else:
        params["customer_email"] = user.email
    return stripe.checkout.Session.create(**params)


def get_event(payload: dict, sig: str) -> Event:
    """Validates a Stripe event to weed out hacked calls"""
    return Webhook.construct_event(payload, sig, CONFIG.stripe_sign_secret)


async def new_subscription(session: dict) -> bool:
    """Create a new subscription for a validated Checkout Session"""
    user = User.find_one(User.id == ObjectId(session["client_reference_id"]))
    if user is None:
        return False
    user.stripe = Stripe(
        customer_id=session["customer"], subscription_id=session["subscription"]
    )
    plan_id = session["display_items"][0]["plan"]["id"]
    user.plan = await Plan.by_stripe_id(plan_id)
    user.new_token(dev=True)
    await user.save()
    return True


async def change_subscription(user: User, plan: Plan) -> bool:
    """Change the subscription from one plan to another"""
    if not user.stripe:
        return False
    sub_id = user.stripe.subscription_id
    if not sub_id or user.plan == plan:
        return False
    sub = Subscription.retrieve(sub_id)
    sub.modify(
        sub_id,
        cancel_at_period_end=False,
        items=[{"id": sub["items"]["data"][0].id, "plan": plan.stripe_id}],
    )
    user.stripe.subscription_id = sub.id
    user.plan = plan
    await user.save()
    return True


async def cancel_subscription(user: User) -> bool:
    """Cancel a subscription"""
    if user.stripe is None:
        return False
    if user.stripe.subscription_id:
        sub = Subscription.retrieve(user.stripe.subscription_id)
        sub.delete()
        user.stripe.subscription_id = None
    user.plan = await Plan.by_key("free")
    user.remove_token_by(type="dev")
    await user.save()
    return True
