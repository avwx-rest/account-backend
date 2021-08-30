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


class UserAddon(AddonOut):
    """Addon fields stored in the user model"""

    price_id: str


class Addon(Document, AddonOut):
    """Plan add-on entitlement"""

    product_id: str
    price_id: Optional[str]
    price_ids: Optional[dict[str, str]]

    class Collection:
        """DB collection name"""

        name = "addon"

    @classmethod
    async def by_key(cls, key: str) -> "Addon":
        """Get an add-on by Stripe product ID"""
        return await cls.find_one(cls.key == key)

    def to_user(self, price_key: str = None) -> UserAddon:
        """Return a user-specific version of the addon"""
        try:
            price = self.price_ids[price_key]
        except (AttributeError, KeyError, TypeError):
            price = self.price_id
        return UserAddon(
            key=self.key,
            name=self.name,
            description=self.description,
            price_id=price,
        )
