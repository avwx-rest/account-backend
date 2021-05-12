"""
"""

from contextlib import suppress
from datetime import datetime, timedelta, timezone
from typing import Optional

import stripe as stripelib
from bson import ObjectId
from pydantic import BaseModel, Field

from account.app import app
from account.models.addon import Addon
from account.models.plan import Plan
from account.models.token import Token


class Stripe(BaseModel):
    customer_id: str
    subscription_id: str


class UserAuth(BaseModel):
    email: str
    password: str

    @classmethod
    def by_email(cls, email: str) -> "User":
        user = app.db.user.find_one({"email": email})
        return cls(**user)


class User(UserAuth):
    active: bool = False
    disabled: bool = False

    email_confirmed_at: Optional[datetime] = None

    # User information
    first_name: str = ""
    last_name: str = ""

    # API and Payment information
    stripe: Optional[Stripe] = None
    plan: Optional[Plan] = None
    tokens: list[Token] = Field(default=[])
    allow_overage: bool = False

    subscribed: bool = False

    @classmethod
    def by_customer_id(cls, id: str) -> "User":
        user = app.db.user.find_one({"stripe.customer_id": id})
        return cls(**user)

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
        return self.id.generation_time

    # @property
    # def stripe_data(self) -> Optional[stripelib.Customer]:
    #     with suppress(AttributeError, stripelib.error.InvalidRequestError):
    #         return stripelib.Customer.retrieve(self.stripe.customer_id)

    @property
    def has_subscription(self) -> bool:
        """Returns True if the user has a Stripe subscription ID"""
        with suppress(AttributeError):
            return isinstance(self.stripe.subscription_id, str)
        return False

    def new_token(self, dev: bool = False) -> bool:
        """Generate a new API token"""
        if self.disabled:
            return False
        if dev:
            for token in self.tokens:
                if token.type == "dev":
                    return False
            token = Token.dev()
        else:
            token = Token.new()
        self.tokens.append(token)
        return True

    def get_token(
        self, value: Optional[str] = None, _id: Optional[ObjectId] = None
    ) -> Optional[str]:
        """Returns a Token matching the token value or id"""
        for token in self.tokens:
            if value and token.value == value:
                return token
            if _id and token._id == _id:
                return token
        return None

    def update_token(self, value: str, name: str, active: bool) -> bool:
        """Update certain fields on a Token matching a token value"""
        for i, token in enumerate(self.tokens):
            if value and token.value == value:
                self.tokens[i].name = name
                self.tokens[i].active = active
                return True
        return False

    def refresh_token(self, value: str):
        """Create a new Token value"""
        for i, token in enumerate(self.tokens):
            if value and token.value == value:
                self.tokens[i].refresh()

    def token_usage(
        self, limit: int = 30, refresh: bool = False
    ) -> dict[ObjectId, dict]:
        """Returns recent token usage counts"""
        if not self.tokens:
            return {}
        target = datetime.now(tz=timezone.utc) - timedelta(days=limit)
        data = app.db.token.aggregate(
            [
                {"$match": {"user_id": self.id, "date": {"$gte": target}}},
                {"$project": {"_id": 0, "date": 1, "count": 1, "token_id": 1}},
                {
                    "$group": {
                        "_id": "$date",
                        "counts": {
                            "$push": {"token_id": "$token_id", "count": "$count"}
                        },
                    }
                },
            ]
        )
        data = {
            i["_id"].date(): {j["token_id"]: j["count"] for j in i["counts"]}
            for i in data
        }
        days = [(target + timedelta(days=i)).date() for i in range(limit)]
        app_tokens = {t._id: [] for t in self.tokens if t.type != "dev"}
        dev_tokens = {t._id: [] for t in self.tokens if t.type == "dev"}
        for day in days:
            tokens = data.get(day, {})
            for token_id in app_tokens:
                app_tokens[token_id].append(tokens.get(token_id, 0))
            for token_id in dev_tokens:
                dev_tokens[token_id].append(tokens.get(token_id, 0))
        ret = {"days": days, "app": app_tokens, "dev": dev_tokens}
        ret["total"] = [sum(i) for i in zip(*app_tokens.values())]
        return ret

    # def remove_token_by(self, value: str = None, type: str = None) -> bool:
    #     """Remove the first token encountered matching a value or type"""
    #     for i, token in enumerate(self.tokens):
    #         if (value and token.value == value) or (type and token.type == type):
    #             self.tokens.pop(i)
    #             return True
    #     return False

    def invoices(self, limit: int = 5) -> list[dict]:
        """Returns the user's recent invoice objects"""
        with suppress(AttributeError, stripelib.error.InvalidRequestError):
            return stripelib.Invoice.list(
                customer=self.stripe.customer_id, limit=limit
            )["data"]
        return []

    def has_addon(self, addon: Addon) -> bool:
        """Returns True if user has an addon in their subscription"""
        with suppress(AttributeError, stripelib.error.InvalidRequestError):
            sub = stripelib.Subscription.retrieve(self.stripe.subscription_id)
            for item in sub["items"]["data"]:
                if item["price"]["id"] == addon.stripe_id:
                    return True
        return False

    def add_addon(self, addon: Addon):
        """Adds an addon to the user's subscription"""
        stripelib.SubscriptionItem.create(
            subscription=self.stripe.subscription_id, price=addon.stripe_id
        )
