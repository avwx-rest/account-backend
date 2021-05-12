"""
"""

from pydantic.dataclasses import dataclass

from account.app import app


@dataclass
class Plan:
    key: str
    name: str
    type: str
    stripe_id: str
    description: str
    price: int
    level: int
    limit: int
    overage: bool = False

    def __repr__(self) -> str:
        return f"<Plan {self.key}>"

    def __str__(self) -> str:
        return self.key

    def __hash__(self) -> int:
        return hash(self.key)

    def __eq__(self, other) -> bool:
        if not other:
            return False
        if isinstance(other, str):
            return self.key == other
        return self.key == other.key

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

    @classmethod
    def by_key(cls, key: str) -> "Plan":
        plan = app.db.plan.find_one({"key": key})
        return cls(**plan)

    @classmethod
    def by_stripe_id(cls, id: str) -> "Plan":
        plan = app.db.plan.find_one({"stripe_id": id})
        return cls(**plan)
