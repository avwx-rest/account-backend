"""
User database and input models
"""

import asyncio as aio
from datetime import datetime
from secrets import token_urlsafe
from typing import Optional

from beanie import Document
from pydantic import BaseModel, EmailStr, Field

from account.models import usersdb
from account.models.plan import Plan, PlanBase


class Stripe(BaseModel):
    """Stripe payment account data"""

    customer_id: str
    subscription_id: Optional[str]


class Token(BaseModel):
    """Primary API account token"""

    name: str
    type: str
    value: str
    active: bool = True

    async def is_unique(self) -> bool:
        """Returns True if token value isn't found in the user collection"""
        resp = await UserDB.find_one({"tokens.value": self.value})
        return resp is None

    def _gen(self):
        value = token_urlsafe(32)
        if self.type == "dev":
            value = "dev-" + value[4:]
        self.value = value

    @classmethod
    async def new(cls, name: str = "Token", type: str = "app"):
        """Generate a new unique token"""
        token = cls(name=name, type=type, value="")
        await token.refresh()
        return token

    @classmethod
    async def dev(cls):
        """Generate a new development token"""
        return await cls.new("Development", "dev")

    async def refresh(self):
        """Refresh the token value"""
        self._gen()
        while not await self.is_unique():
            self._gen()


class User(usersdb.BaseUser, Document):
    """Public fields returned about a user"""

    class Collection:
        name = "userrr"

    # User information
    first_name: Optional[str]
    last_name: Optional[str]

    # API and Payment information
    plan: Optional[PlanBase]
    stripe: Optional[Stripe]
    tokens: list[Token] = Field(default=[])
    allow_overage: bool = False


class UserCreate(usersdb.CreateUpdateDictModel):
    """Fields necessary to create a new user"""

    email: EmailStr
    password: str


class UserUpdate(User, usersdb.BaseUserUpdate):
    """Fields the user is allowed to update"""


class UserDB(User, usersdb.BaseUserDB):
    """Includes private fields in the database model"""

    email_confirmed_at: Optional[datetime]

    async def set_new_user_defaults(self):
        """Fill computed defaults for a new user"""
        # tasks = [Plan.default_base(), Token.new()]
        # plan, token = await aio.gather(*tasks)
        plan = await Plan.default_base()
        await self.update({"$set": {
            UserDB.plan: plan.dict(),
            # UserDB.tokens: [token.dict()],
        }})
