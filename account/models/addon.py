"""
Plan add-on models
"""

# pylint: disable=too-few-public-methods

from typing import Optional

from beanie import Document
from pydantic import BaseModel


class AddonOut(BaseModel):
    """Addon fields returned to the user"""

    key: str
    name: str
    description: str
    documentation: Optional[str]


class UserAddon(AddonOut):
    """Addon fields stored in the user model"""

    price_id: str


class Addon(Document, AddonOut):
    """Plan add-on entitlement"""

    product_id: str
    price_ids: Optional[dict[str, str]]

    class Collection:
        """DB collection name"""

        name = "addon"

    @classmethod
    async def by_key(cls, key: str) -> "Addon":
        """Get an add-on by internal key"""
        return await cls.find_one(cls.key == key)

    @classmethod
    async def by_product_id(cls, key: str) -> "Addon":
        """Get an add-on by Stripe product ID"""
        return await cls.find_one(cls.product_id == key)

    def to_user(self, plan: str) -> UserAddon:
        """Return a user-specific version of the addon"""
        try:
            price = self.price_ids[plan]
        except (AttributeError, KeyError, TypeError):
            key = "yearly" if plan.endswith("-year") else "monthly"
            price = self.price_ids[key]
        return UserAddon(
            key=self.key,
            name=self.name,
            description=self.description,
            price_id=price,
        )
