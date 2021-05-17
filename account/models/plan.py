"""
Plan document and embedded field
"""

from typing import Optional

from beanie import Document, Indexed
from pydantic import BaseModel


class PlanBase(BaseModel):
    """Plan embedded in the User model"""

    key: Indexed(str, unique=True)
    name: str
    type: str
    description: str
    price: int
    level: int
    limit: int
    stripe_id: Optional[str]


class Plan(Document, PlanBase):
    """Plan document of primary tiers"""

    class Collection:
        name = "plan"

    @classmethod
    async def default_base(self) -> PlanBase:
        """Returns the default "free" embedded plan"""
        plan = await Plan.find_one(Plan.key == "free")
        return plan.as_embedded()

    def as_embedded(self) -> PlanBase:
        """Returns the Plan document as an embedded plan"""
        data = {k: getattr(self, k) for k in self.__fields_set__}
        return PlanBase(**data)
