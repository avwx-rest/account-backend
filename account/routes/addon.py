"""Addon router."""

from fastapi import APIRouter, Depends, HTTPException, Response

from account.models.addon import Addon, AddonOut, UserAddon
from account.models.user import User
from account.util.current_user import current_user
from account.util.stripe import (
    get_session,
    add_to_subscription,
    remove_from_subscription,
)

router = APIRouter(prefix="/addon", tags=["Addon"])


@router.get("", response_model=list[AddonOut])
async def get_user_addons(user: User = Depends(current_user)) -> list[UserAddon]:
    """Return the current user's addons."""
    return user.addons


@router.post("/{key}")
async def new_addon(  # type: ignore[no-untyped-def]
    key: str, user: User = Depends(current_user)
):
    """Add a new addon to user by key. Returns a Stripe session if Checkout is required."""
    addon = await Addon.by_key(key)
    if addon is None:
        raise HTTPException(404, f"Addon with key {key} does not exist")
    if user.has_addon(addon.key):
        raise HTTPException(400, f"User already has the {addon.key} addon")
    if user.plan is None:
        raise ValueError("Cannot add addon to user with no plan")
    user_addon = addon.to_user(user.plan.key)
    if not user.has_subscription:
        return get_session(user, user_addon.price_id, metered=addon.metered)
    if not add_to_subscription(user, user_addon.price_id):
        raise HTTPException(500, "Unable to add addon to user subscription")
    user.addons.append(user_addon)
    if addon.key == "overage":
        user.allow_overage = True
    await user.save()
    return None


@router.delete("/{key}")
async def delete_addon(key: str, user: User = Depends(current_user)) -> Response:
    """Remove an addon from a user's subscription."""
    for item in user.addons:
        if item.key == key:
            addon = item
            break
    else:
        raise HTTPException(400, f"User does not have the {key} addon")
    if not remove_from_subscription(user, addon.price_id):
        raise HTTPException(500, "Unable to remove addon from user subscription")
    user.addons = [i for i in user.addons if i.key != key]
    if addon.key == "overage":
        user.allow_overage = False
    await user.save()
    return Response(status_code=204)


@router.get("/all", response_model=list[AddonOut])
async def get_addons() -> list[Addon]:
    """Return all addons."""
    return await Addon.all().to_list()
