from typing import Any, Optional

import jwt
from bson import ObjectId

from fastapi_users.db.base import BaseUserDatabase
from fastapi_users.models import BaseUserDB
from fastapi_users.utils import JWT_ALGORITHM

from fastapi_users.authentication import JWTAuthentication as _JWTAuth
from fastapi_users.db import MongoDBUserDatabase as _MongoUserDB
from fastapi_users.models import UD


class MongoDBUserDatabase(_MongoUserDB):

    async def get(self, id: ObjectId) -> Optional[UD]:
        user = await self.collection.find_one({"_id": id})
        return self.user_db_model(**user) if user else None

    async def update(self, user: UD) -> UD:
        await self.collection.replace_one({"_id": user.id}, user.dict())
        return user

    async def delete(self, user: UD) -> None:
        await self.collection.delete_one({"_id": user.id})


class JWTAuthentication(_JWTAuth):

    async def __call__(
        self,
        credentials: Optional[str],
        user_db: BaseUserDatabase,
    ) -> Optional[BaseUserDB]:
        if credentials is None:
            return None

        try:
            data = jwt.decode(
                credentials,
                self.secret,
                audience=self.token_audience,
                algorithms=[JWT_ALGORITHM],
            )
            user_id = data.get("user_id")
            if user_id is None:
                return None
        except jwt.PyJWTError:
            return None

        try:
            return await user_db.get(ObjectId(user_id))
        except ValueError:
            return None
