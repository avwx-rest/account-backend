"""
Stripe subscription utilities
"""

import stripe
from stripe import Event, Subscription, Webhook

from account.config import CONFIG
from account.models.addon import Addon
from account.models.plan import Plan
from account.models.user import Stripe, User, UserToken
from account.util import mail


stripe.api_key = CONFIG.stripe_secret_key

_SESSION = {
    "payment_method_types": ["card"],
    "success_url": f"{CONFIG.root_url}/stripe/success",
    "cancel_url": f"{CONFIG.root_url}/stripe/cancel",
}


def get_session(user: User, price_id: str) -> stripe.checkout.Session:
    """Creates a Stripe Session object to start a Checkout"""
    params = {
        "client_reference_id": user.id,
        "subscription_data": {"items": [{"plan": price_id}]},
        **_SESSION,
    }
    if user.stripe:
        params["customer"] = user.stripe.customer_id
    else:
        params["customer_email"] = user.email
    return stripe.checkout.Session.create(**params)  # type: ignore[arg-type]


def get_event(payload: dict, sig: str) -> Event:
    """Validates a Stripe event to weed out hacked calls"""
    event: Event = Webhook.construct_event(payload, sig, CONFIG.stripe_sign_secret)
    return event


def get_portal_session(user: User) -> stripe.billing_portal.Session:
    """Creates a Stripe billing portal session"""
    if user.stripe is None:
        raise ValueError("Cannot create billing session without stripe info")
    return stripe.billing_portal.Session.create(
        customer=user.stripe.customer_id,
        return_url=f"{CONFIG.root_url}/plans",
    )


async def new_subscription(session: dict) -> bool:
    """Create a new subscription for a validated Checkout Session"""
    user = await User.from_stripe_session(session)
    if user is None or user.plan is None:
        return False
    user.stripe = Stripe(
        customer_id=session["customer"], subscription_id=session["subscription"]
    )
    item = session["display_items"][0]["plan"]
    if plan := await Plan.by_stripe_id(item["id"]):
        user.plan = plan
        token = await UserToken.new(type="dev")
        user.tokens.append(token)
    elif addon := await Addon.by_product_id(item["product"]):
        user.addons.append(addon.to_user(user.plan.key))
    else:
        return False
    await user.save()
    return True


async def change_subscription(user: User, plan: Plan) -> bool:
    """Change the subscription from one plan to another"""
    if not user.stripe:
        return False
    sub_id = user.stripe.subscription_id
    if not sub_id or user.plan == plan:
        return False
    items: list[dict] = []
    sub = Subscription.retrieve(sub_id)
    # Update existing subscription items
    for item in sub["items"]["data"]:
        if addon := await Addon.by_product_id(item["price"]["product"]):
            user_addon = addon.to_user(plan.key)
            if user_addon.price_id != item["price"]["id"]:
                user.replace_addon(user_addon)
                items.append({"id": item["id"], "price": user_addon.price_id})
        else:
            # This updates an existing paid plan
            items.append({"id": item["id"], "plan": plan.stripe_id})
    sub.modify(
        sub_id,
        cancel_at_period_end=False,
        items=items,
    )
    # This adds a paid plan if coming from a free one after modifying any addons
    if user.plan and not user.plan.stripe_id and plan.stripe_id:
        add_to_subscription(user, plan.stripe_id)
    user.stripe.subscription_id = sub.id
    user.plan = plan
    await user.save()
    return True


async def cancel_subscription(user: User, keep_addons: bool = False) -> bool:
    """Cancel a subscription"""
    if user.stripe is None or user.plan is None:
        return False
    if user.stripe.subscription_id:
        if keep_addons and not remove_from_subscription(user, user.plan.stripe_id):
            return False
        if Subscription.delete(user.stripe.subscription_id)["ended_at"]:  # type: ignore[arg-type]
            user.stripe.subscription_id = None
            user.addons = []
    user.plan = await Plan.by_key("free")
    user.tokens = [t for t in user.tokens if t.type != "dev"]
    await user.save()
    return True


def add_to_subscription(user: User, price_id: str) -> bool:
    """Add an addon to an existing subscription"""
    if not user.has_subscription or user.stripe is None:
        return False
    stripe.SubscriptionItem.create(
        subscription=user.stripe.subscription_id, price=price_id
    )
    return True


def remove_from_subscription(user: User, price_id: str | None = None) -> bool:
    """Remove an addon from a subscription"""
    if (
        not user.has_subscription
        or user.stripe is None
        or user.stripe.subscription_id is None
    ):
        return False
    sub = Subscription.retrieve(user.stripe.subscription_id)
    for item in sub["items"]["data"]:
        if item["price"]["id"] == price_id:
            # If nothing left in subscription
            if len(sub["items"]["data"]) == 1:
                if stripe.Subscription.delete(user.stripe.subscription_id)["ended_at"]:  # type: ignore[arg-type]
                    user.stripe = None
                    return True
            else:
                options = {}
                if item["plan"]["usage_type"] == "metered":
                    options["clear_usage"] = True
                return (
                    stripe.SubscriptionItem.delete(item["id"], **options)["deleted"]
                    is True
                )
    return False


def update_email(user: User, new_email: str) -> bool:
    """Update the email associated with the Stripe user"""
    if not user.has_subscription or user.stripe is None:
        return False
    stripe.Customer.modify(user.stripe.customer_id, email=new_email)
    return True


async def invoice_paid(invoice: dict) -> bool:
    """Re-enable a user account after invoice payment"""
    user = await User.by_customer_id(invoice["customer"])
    if user is None:
        return False
    if user.disabled:
        user.disabled = False
        await user.save()
        await mail.send_enabled_email(user.email)
    return True


async def invoice_failed(invoice: dict) -> bool:
    """Disable user account if two or more failed invoices"""
    if invoice["paid"]:
        return True
    attempts = invoice["attempt_count"]
    if attempts < 1:
        return True
    user = await User.by_customer_id(invoice["customer"])
    if user is None:
        return False
    url = get_portal_session(user).url
    if attempts == 1:
        await mail.send_disable_email(user.email, url, warning=True)
        return True
    user.disabled = True
    await user.save()
    await mail.send_disable_email(user.email, url)
    return True
