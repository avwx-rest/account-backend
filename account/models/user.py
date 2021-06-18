"""
User models
"""

# pylint: disable=too-few-public-methods,redefined-builtin,invalid-name

from datetime import datetime
from secrets import token_urlsafe
from typing import Optional

from beanie import Document, Indexed
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

from account.models.addon import Addon
from account.models.plan import Plan, PlanOut


class Stripe(BaseModel):
    """Stripe IDs"""

    customer_id: str
    subscription_id: str


class Token(BaseModel):
    """API token"""

    _id: ObjectId
    name: str
    type: str
    value: str
    active: bool = True

    async def is_unique(self) -> bool:
        """Checks if the current token.value is unique"""
        resp = await User.find_one(User.tokens.value == self.value, {"_id": 1})
        return resp is None

    def _gen(self):
        value = token_urlsafe(32)
        if self.type == "dev":
            value = "dev-" + value[4:]
        self.value = value

    @classmethod
    async def new(cls, name: str = "Token", type: str = "app"):
        """Generate a new unique token"""
        token = cls(_id=ObjectId(), name=name, type=type, value="")
        await token.refresh()
        return token

    @classmethod
    def dev(cls):
        """Generate a new development token"""
        return cls.new("Development", "dev")

    async def refresh(self):
        """Refresh the token value"""
        self._gen()
        unique = await self.is_unique()
        while not unique:
            self._gen()
            unique = await self.is_unique()


class UserAuth(BaseModel):
    """User register and login auth"""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User-updatable fields"""

    email: EmailStr

    # User information
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserOut(UserUpdate):
    """User fields returned to the user"""

    email: Indexed(EmailStr, unique=True)

    # API and Payment information
    stripe: Optional[Stripe] = None
    plan: Optional[PlanOut] = None
    tokens: list[Token] = Field(default=[])
    addons: list[Addon] = Field(default=[])
    allow_overage: bool = False

    subscribed: bool = False
    disabled: bool = False


class User(Document, UserOut):
    """User DB representation"""

    password: str
    email_confirmed_at: Optional[datetime] = None
    plan: Optional[Plan] = None

    class Collection:
        """DB collection name"""

        name = "userrr"

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    def __str__(self) -> str:
        return self.email

    def __hash__(self) -> int:
        return hash(self.email)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, User):
            return self.email == other.email
        return False

    @property
    def created(self) -> datetime:
        """Datetime user was created from ID"""
        return self.id.generation_time

    @classmethod
    async def by_email(cls, email: str) -> "User":
        """Get a user by email"""
        return await cls.find_one(cls.email == email)

    @classmethod
    async def by_customer_id(cls, id: str) -> "User":
        """Get a user by Stripe customer ID"""
        return await cls.find_one(cls.stripe.customer_id == id)

    async def add_default_documents(self) -> None:
        """Adds initial embedded documents"""
        self.plan = await Plan.by_key("free")
