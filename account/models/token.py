"""
Token models
"""

# pylint: disable=too-few-public-methods

from datetime import date, datetime
from typing import Optional

from beanie import Document, PydanticObjectId
from bson.objectid import ObjectId
from pydantic import BaseModel, Field

from account.models.helpers import ObjectIdStr


class TokenUpdate(BaseModel):
    """Updatable token fields"""

    name: Optional[str] = None
    active: Optional[bool] = None


class Token(BaseModel):
    """Token fields returned to the user"""

    id: ObjectIdStr = Field(default_factory=ObjectId, alias="_id")
    name: str
    type: str
    value: str
    active: bool = True


class TokenUsageOut(BaseModel):
    """Token usage fields returned to the user"""

    count: int
    date: date


class TokenUsage(Document, TokenUsageOut):
    """Token usage DB representation"""

    token_id: PydanticObjectId
    user_id: PydanticObjectId
    date: datetime
    updated: datetime

    class Collection:
        """DB collection name"""

        name = "token"


class AllTokenUsageOut(BaseModel):
    """Token usage including the ID"""

    token_id: PydanticObjectId
    days: list[TokenUsageOut]
