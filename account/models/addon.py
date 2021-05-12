"""
"""

from pydantic import BaseModel
from account.app import app


class Addon(BaseModel):
    """"""

    key: str
    stripe_id: str

    @classmethod
    def by_key(cls, key: str) -> "Addon":
        addon = app.db.addon.find_one({"key": key})
        return cls(**addon)
