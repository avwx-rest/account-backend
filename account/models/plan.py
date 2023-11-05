"""
Pricing plan models
"""

from typing import Annotated, Any, Optional

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

    def __eq__(self, other: Any) -> bool:
        if not other:
            return False
        if isinstance(other, str):
            return self.key == other
        if isinstance(other, PlanOut):
            return self.key == other.key
        raise ValueError

    def __lt__(self, other: Any) -> bool:
        if other is None:
            return False
        if isinstance(other, int):
            return self.level < other
        if isinstance(other, PlanOut):
            return self.level < other.level
        raise ValueError

    def __gt__(self, other: Any) -> bool:
        if other is None:
            return True
        if isinstance(other, int):
            return self.level > other
        if isinstance(other, PlanOut):
            return self.level > other.level
        raise ValueError


class Plan(Document, PlanOut):
    """Plan DB representation"""

    key: Annotated[str, Indexed(str, unique=True)]
    stripe_id: str | None = None

    class Settings:
        """DB collection name"""

        name = "plan"

    @classmethod
    async def by_key(cls, key: str) -> Optional["Plan"]:
        """Get a plan by key"""
        return await cls.find_one(cls.key == key)

    @classmethod
    async def by_stripe_id(cls, id: str) -> Optional["Plan"]:
        """Get a plan by Stripe product ID"""
        return await cls.find_one(cls.stripe_id == id)
