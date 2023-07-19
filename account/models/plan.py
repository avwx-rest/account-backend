"""
Pricing plan models
"""

# pylint: disable=too-few-public-methods,redefined-builtin,invalid-name

from typing import Optional

from beanie import Document, Indexed
from pydantic import BaseModel


class PlanOut(BaseModel):
    """Plan fields returned to the user"""

    key: str
    name: str
    type: str
    description: str
    price: int
    level: int
    limit: int

    def __repr__(self) -> str:
        return f"<Plan {self.key}>"

    def __str__(self) -> str:
        return self.key

    def __hash__(self) -> int:
        return hash(self.key)

    def __eq__(self, other) -> bool:
        if not other:
            return False
        return self.key == other if isinstance(other, str) else self.key == other.key

    def __lt__(self, other) -> bool:
        if other is None:
            return False
        if isinstance(other, int):
            return self.level < other
        return self.level < other.level

    def __gt__(self, other) -> bool:
        if other is None:
            return True
        if isinstance(other, int):
            return self.level > other
        return self.level > other.level


class Plan(Document, PlanOut):
    """Plan DB representation"""

    key: Indexed(str, unique=True)
    stripe_id: Optional[str] = None

    class Collection:
        """DB collection name"""

        name = "plan"

    @classmethod
    async def by_key(cls, key: str) -> "Plan":
        """Get a plan by key"""
        return await cls.find_one(cls.key == key)

    @classmethod
    async def by_stripe_id(cls, id: str) -> "Plan":
        """Get a plan by Stripe product ID"""
        return await cls.find_one(cls.stripe_id == id)
