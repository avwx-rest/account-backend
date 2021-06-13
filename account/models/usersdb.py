"""
FastAPI-Users BaseModel replacements

Removes the id: UUID field that conflicts with Mongo/Beanie
"""

from typing import Optional

from pydantic import BaseModel, EmailStr


class CreateUpdateDictModel(BaseModel):
    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "_id",
                "is_superuser",
                "is_active",
                "is_verified",
                "oauth_accounts",
            },
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"_id"})


class BaseUser(CreateUpdateDictModel):
    """Base User model."""

    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class BaseUserCreate(CreateUpdateDictModel):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class BaseUserUpdate(BaseUser):
    password: Optional[str]


class BaseUserDB(BaseUser):
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool
    hashed_password: str

    class Config:
        orm_mode = True
