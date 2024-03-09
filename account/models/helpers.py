"""Pydantic helper types."""

from collections.abc import Callable, Iterator
from typing import Any

from bson.objectid import ObjectId, InvalidId


class ObjectIdStr(str):
    """Represents an ObjectId not managed by Beanie."""

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable[[Any, Any], str]]:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any, _: Any) -> str:
        """Validate potential ObjectId value."""
        try:
            ObjectId(str(value))
        except InvalidId as exc:
            raise ValueError("Not a valid ObjectId") from exc
        return str(value)
