"""Plan add-on models."""

from typing import Self

from beanie import Document
from pydantic import BaseModel


class AddonOut(BaseModel):
    """Addon fields returned to the user."""

    key: str
    name: str
    description: str
    documentation: str | None = None


class UserAddon(AddonOut):
    """Addon fields stored in the user model."""

    price_id: str


class Addon(Document, AddonOut):
    """Plan add-on entitlement."""

    product_id: str
    price_ids: dict[str, str]
    metered: bool

    class Settings:
        """DB collection name."""

        name = "addon"

    @classmethod
    async def by_key(cls, key: str) -> Self | None:
        """Get an add-on by internal key."""
        return await cls.find_one(cls.key == key)

    @classmethod
    async def by_product_id(cls, key: str) -> Self | None:
        """Get an add-on by Stripe product ID."""
        return await cls.find_one(cls.product_id == key)

    def to_user(self, plan: str) -> UserAddon:
        """Return a user-specific version of the addon."""
        price = self.price_ids.get(plan)
        if not price:
            key = "yearly" if plan.endswith("-year") else "monthly"
            price = self.price_ids.get(key)
        if not price:
            msg = f"Unknown addon price for {plan} and {key}"
            raise ValueError(msg)
        return UserAddon(
            key=self.key,
            name=self.name,
            description=self.description,
            documentation=self.documentation,
            price_id=price,
        )
