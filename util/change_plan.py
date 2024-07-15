"""Update a user's plan information."""

import asyncio as aio

import typer
from loader import load_models

from account.models.addon import Addon
from account.models.user import Plan, User
from account.util.stripe import cancel_subscription, change_subscription


async def _change_plan(user: User, plan: Plan, *, remove_addons: bool) -> int:
    if user.plan and user.plan.key == plan.key:
        print(f"User is already subscribed to the {plan.name} plan")
        return 2
    if plan.stripe_id:
        print("Move to paid")
        if not user.has_subscription:
            msg = "Free to paid flow requires Dashboard access"
            raise NotImplementedError(msg)
        if not await change_subscription(user, plan):
            print("Unable to update your subscription")
            return 3
    elif not await cancel_subscription(user, keep_addons=not remove_addons):
        print("Unable to cancel your subscription")
        return 4
    return 0


async def main(email: str, plan: str, *, remove_addons: bool) -> int:
    """Update a user's plan information."""
    await load_models(Addon, Plan, User)

    user = await User.by_email(email)
    if not user:
        print(f"User with email {email} does not exist")
        return 1

    plan_obj = await Plan.by_key(plan)
    if plan_obj is None:
        print(f"Plan with key {plan} does not exist")
        return 1

    return await _change_plan(user, plan_obj, remove_addons=remove_addons)


def change_plan(email: str, plan: str, remove_addons: bool = True) -> int:  # noqa FBT001
    """Change a user's plan details."""
    return aio.run(main(email, plan, remove_addons=remove_addons))


if __name__ == "__main__":
    typer.run(change_plan)
