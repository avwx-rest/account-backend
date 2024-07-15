"""User models."""

from datetime import UTC, datetime
from secrets import token_urlsafe
from typing import Annotated, Any, Self

from beanie import Document, Indexed
from bson.objectid import ObjectId
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field
from stripe.checkout import Session

from account.models.addon import AddonOut, UserAddon
from account.models.helpers import ObjectIdStr
from account.models.plan import Plan, PlanOut
from account.models.token import Token


class Stripe(BaseModel):
    """Stripe IDs."""

    customer_id: str
    subscription_id: str | None


class Notification(BaseModel):
    """User notification."""

    type: str
    text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    id: ObjectIdStr = Field(default_factory=ObjectId)


class UserToken(Token):
    """API token."""

    async def is_unique(self) -> bool:
        """Check if the current token.value is unique."""
        resp = await User.find_one(User.tokens.value == self.value, {"_id": 1})  # type: ignore[attr-defined]
        return resp is None

    def _gen(self) -> None:
        value = token_urlsafe(32)
        if self.type == "dev":
            value = f"dev-{value[4:]}"
        self.value = value

    @classmethod
    async def new(cls, name: str = "Token", type: str = "app") -> Self:  # noqa A002
        """Generate a new unique token."""
        token = cls(_id=ObjectId(), name=name, type=type, value="")  # type: ignore[arg-type]
        await token.refresh()
        return token

    @classmethod
    async def dev(cls) -> Self:
        """Generate a new development token."""
        return await cls.new("Development", "dev")

    async def refresh(self) -> None:
        """Refresh the token value."""
        self._gen()
        unique = await self.is_unique()
        while not unique:
            self._gen()
            unique = await self.is_unique()


class UserAuth(BaseModel):
    """User register and login auth."""

    email: EmailStr
    password: str


class UserRegister(UserAuth):
    """Registration include reCaptcha token."""

    token: str


class UserUpdate(BaseModel):
    """Updatable user fields."""

    email: EmailStr | None = None

    # User information
    first_name: str | None = None
    last_name: str | None = None


class UserOut(UserUpdate):
    """User fields returned to the user."""

    email: Annotated[str, Indexed(EmailStr, unique=True)]

    # API and Payment information
    stripe: Stripe | None = None
    plan: PlanOut | None = None
    tokens: list[UserToken] = Field(default=[])
    addons: list[AddonOut] = Field(default=[])
    notifications: list[Notification] = Field(default=[])

    allow_overage: bool = False
    subscribed: bool = False
    disabled: bool = False
    is_admin: bool = False


class User(Document, UserOut):
    """User DB representation."""

    password: str
    email_confirmed_at: datetime | None = None
    plan: Plan | None = None
    addons: list[UserAddon] = Field(default=[])  # type: ignore[assignment]
    old_emails: list[EmailStr] | None = None

    class Settings:
        """DB collection name."""

        name = "user"

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    def __str__(self) -> str:
        return self.email

    def __hash__(self) -> int:
        return hash(self.email)

    def __eq__(self, other: object) -> bool:
        return self.email == other.email if isinstance(other, User) else False

    @property
    def created(self) -> datetime | None:
        """Datetime user was created from ID."""
        return self.id.generation_time if self.id else None

    @property
    def has_subscription(self) -> bool:
        """Return True if the user has a Stripe subscript ID."""
        return isinstance(self.stripe.subscription_id, str) if self.stripe else False

    @property
    def jwt_subject(self) -> dict[str, Any]:
        """JWT subject fields."""
        return {"username": self.email}

    @classmethod
    async def by_email(cls, email: str) -> Self | None:
        """Get a user by email."""
        return await cls.find_one(cls.email == email)

    @classmethod
    async def by_customer_id(cls, user_id: str) -> Self | None:
        """Get a user by Stripe customer ID."""
        return await cls.find_one(cls.stripe.customer_id == user_id)  # type: ignore

    @classmethod
    async def from_stripe_session(cls, session: Session) -> Self | None:
        """Get a user from a Stripe event session."""
        return await User.get(ObjectId(session.client_reference_id))

    async def add_default_documents(self) -> None:
        """Add initial embedded documents."""
        self.plan = await Plan.by_key("free")

    def get_token(self, value: str) -> tuple[int, UserToken | None]:
        """Return a token and index by its id."""
        return next(
            ((i, token) for i, token in enumerate(self.tokens) if str(token.id) == value),
            (-1, None),
        )

    def get_notification(self, value: str) -> tuple[int, Notification | None]:
        """Return a notification and index by its string value."""
        return next(
            ((i, notification) for i, notification in enumerate(self.notifications) if notification.id == value),
            (-1, None),
        )

    async def add_notification(self, type: str, text: str) -> None:  # noqa A002
        """Add a new notification to the user's list."""
        self.notifications.append(Notification(type=type, text=text))
        await self.save()

    def has_addon(self, key: str) -> bool:
        """Return True if the user has an addon with a matching key."""
        return any(addon.key == key for addon in self.addons)

    def replace_addon(self, addon: UserAddon) -> None:
        """Replace and Addon with the same key value."""
        self.addons = [a for a in self.addons if a.key != addon.key]
        self.addons.append(addon)

    def update_email(self, new_email: str) -> None:
        """Update email logging and replace."""
        if self.old_emails is None:
            self.old_emails = []
        self.old_emails.append(self.email)
        self.email = new_email

    def validate_email(self) -> None:
        """Confirm the user's email address."""
        if self.email_confirmed_at is not None:
            raise HTTPException(400, "Email is already verified")
        if self.disabled:
            raise HTTPException(400, "Your account is disabled")
        self.email_confirmed_at = datetime.now(tz=UTC)
