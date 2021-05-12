"""
"""

# stdlib
from secrets import token_urlsafe

# library
from bson import ObjectId
from pydantic import BaseModel

# module
from account.app import app


class Token(BaseModel):
    _id: ObjectId
    name: str
    type: str
    value: str
    active: bool = True

    @property
    def is_unique(self) -> bool:
        resp = app.db.user.find_one({"tokens.value": self.value}, {"_id": 1})
        return resp is None

    def _gen(self):
        value = token_urlsafe(32)
        if self.type == "dev":
            value = "dev-" + value[4:]
        self.value = value

    @classmethod
    def new(cls, name: str = "Token", type: str = "app"):
        """Generate a new unique token"""
        token = cls(_id=ObjectId(), name=name, type=type, value="")
        token.refresh()
        return token

    @classmethod
    def dev(cls):
        """Generate a new development token"""
        return cls.new("Development", "dev")

    def refresh(self):
        """Refresh the token value"""
        self._gen()
        while not self.is_unique:
            self._gen()
