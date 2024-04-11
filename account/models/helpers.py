"""Pydantic helper types."""

from collections.abc import Callable, Iterator
from typing import Any

from bson.objectid import ObjectId, InvalidId
# from pydantic_core import core_schema
# from pydantic import GetCoreSchemaHandler


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

    # Pydantic v2 -> v3 requirement
    # Necessary to allow OpenAPI spec to build
    # @classmethod
    # def __get_pydantic_core_schema__(
    #     cls, source: type[Any], handler: GetCoreSchemaHandler
    # ) -> core_schema.CoreSchema:
    #     assert issubclass(source, ObjectIdStr)
    #     return core_schema.json_or_python_schema(
    #         json_schema=core_schema.str_schema(),
    #         python_schema=core_schema.is_instance_schema(str),
    #         serialization=core_schema.plain_serializer_function_ser_schema(lambda c: c),
    #     )
