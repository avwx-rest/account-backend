"""
Plan add-on models
"""

# pylint: disable=too-few-public-methods

from beanie import Document


class Addon(Document):
    """Plan add-on entitlement"""

    key: str
    stripe_id: str

    class Collection:
        """DB collection name"""

        name = "addon"

    @classmethod
    async def by_key(cls, key: str) -> "Addon":
        """Get an add-on by Stripe product ID"""
        return await cls.find_one(cls.key == key)
