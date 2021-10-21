"""
User models
"""

# pylint: disable=too-few-public-methods,redefined-builtin,invalid-name

from contextlib import suppress
from datetime import datetime, timezone
from secrets import token_urlsafe
from typing import Optional

from beanie import Document, Indexed
from bson.objectid import ObjectId
from pydantic import BaseModel, EmailStr, Field

from account.models.addon import AddonOut, UserAddon
from account.models.helpers import ObjectIdStr
from account.models.plan import Plan, PlanOut
from account.models.token import Token


class Stripe(BaseModel):
    """Stripe IDs"""

    customer_id: str
    subscription_id: Optional[str]


class Notification(BaseModel):
    """User notification"""

    type: str
    text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    id: ObjectIdStr = Field(default_factory=ObjectId)


class UserToken(Token):
    """API token"""

    id: ObjectIdStr = Field(default_factory=ObjectId, alias="_id")

    async def is_unique(self) -> bool:
        """Checks if the current token.value is unique"""
        resp = await User.find_one(User.tokens.value == self.value, {"_id": 1})
        return resp is None

    def _gen(self):
        value = token_urlsafe(32)
        if self.type == "dev":
            value = "dev-" + value[4:]
        self.value = value  # pylint: disable=attribute-defined-outside-init

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
    """Updatable user fields"""

    email: Optional[EmailStr] = None

    # User information
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserOut(UserUpdate):
    """User fields returned to the user"""

    email: Indexed(EmailStr, unique=True)

    # API and Payment information
    stripe: Optional[Stripe] = None
    plan: Optional[PlanOut] = None
    tokens: list[UserToken] = Field(default=[])
    addons: list[AddonOut] = Field(default=[])
    notifications: list[Notification] = Field(default=[])

    allow_overage: bool = False
    subscribed: bool = False
    disabled: bool = False


class User(Document, UserOut):
    """User DB representation"""

    password: str
    email_confirmed_at: Optional[datetime] = None
    plan: Optional[Plan] = None
    addons: list[UserAddon] = Field(default=[])

    class Collection:
        """DB collection name"""

        name = "user"

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

    @property
    def has_subscription(self) -> bool:
        """Returns True if the user has a Stripe subscript ID"""
        with suppress(AttributeError):
            return isinstance(self.stripe.subscription_id, str)
        return False

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

    def get_token(self, value: str) -> tuple[int, Optional[UserToken]]:
        """Returns a token and index by its string value"""
        for i, token in enumerate(self.tokens):
            if token.value == value:
                return i, token
        return -1, None

    def get_notification(self, value: str) -> tuple[int, Optional[Notification]]:
        """Returns a notification and index by its string value"""
        for i, notification in enumerate(self.notifications):
            if notification.id == value:
                return i, notification
        return -1, None

    async def add_notification(self, type: str, text: str):
        """Add a new notification to the user's list"""
        self.notifications.append(Notification(type=type, text=text))
        await self.save()

    def has_addon(self, key: str) -> bool:
        """Returns True if the user has an addon with a matching key"""
        for addon in self.addons:
            if addon.key == key:
                return True
        return False

    def replace_addon(self, addon: UserAddon) -> None:
        """Replaces and Addon with the same key value"""
        self.addons = [a for a in self.addons if a.key != addon.key]
        self.addons.append(addon)
