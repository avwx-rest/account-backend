"""
Pydantic helper types
"""

from bson.objectid import ObjectId, InvalidId


class ObjectIdStr(str):
    """Represents an ObjectId not managed by Beanie"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """Validate potential ObjectId value"""
        try:
            ObjectId(str(value))
        except InvalidId as exc:
            raise ValueError("Not a valid ObjectId") from exc
        return str(value)
