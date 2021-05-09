"""
Authentication Manager
"""

# Initial implementation from:
# https://github.com/rohanshiva/Deta-FastAPI-JWT-Auth-Blog

# stdlib
import os
from datetime import datetime, timedelta
from functools import wraps

# library
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

SECURITY = HTTPBearer()


class Auth:
    """Authentication Manager"""

    hasher = CryptContext(schemes=["bcrypt"])
    secret = os.getenv("APP_SECRET_STRING", "SUPERSECRET")

    def encode_password(self, password: str) -> str:
        """Returns the hashed password"""
        return self.hasher.hash(password)

    def verify_password(self, password: str, encoded_password: str) -> bool:
        """Returns True if hashed passwords match"""
        return self.hasher.verify(password, encoded_password)

    def encode_token(self, username: str) -> bytes:
        now = datetime.utcnow()
        payload = {
            "exp": now + timedelta(days=0, minutes=30),
            "iat": now,
            "scope": "access_token",
            "sub": username,
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def decode_token(self, token: str) -> str:
        """"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            if payload["scope"] == "access_token":
                return payload["sub"]
            raise HTTPException(
                status_code=401, detail="Scope for the token is invalid"
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def encode_refresh_token(self, username: str) -> bytes:
        """"""
        now = datetime.utcnow()
        payload = {
            "exp": now + timedelta(days=0, hours=10),
            "iat": now,
            "scope": "refresh_token",
            "sub": username,
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def refresh_token(self, refresh_token: str) -> str:
        """Refreshes token or raise HTTP exception"""
        try:
            payload = jwt.decode(refresh_token, self.secret, algorithms=["HS256"])
            if payload["scope"] == "refresh_token":
                username = payload["sub"]
                new_token = self.encode_token(username)
                return new_token
            raise HTTPException(status_code=401, detail="Invalid scope for token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")


AUTH = Auth()


def auth_required(handler):
    """View requires JWT authentication"""

    async def wrapper(
        credentials: HTTPAuthorizationCredentials = Security(SECURITY), *args, **kwargs
    ):
        token = credentials.credentials
        if AUTH.decode_token(token):
            await handler(*args, **kwargs)

    # Fix signature of wrapper
    import inspect

    wrapper.__signature__ = inspect.Signature(
        parameters=[
            # Use all parameters from handler
            *inspect.signature(handler).parameters.values(),
            # Skip *args and **kwargs from wrapper parameters:
            *filter(
                lambda p: p.kind
                not in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                ),
                inspect.signature(wrapper).parameters.values(),
            ),
        ],
        return_annotation=inspect.signature(handler).return_annotation,
    )

    return wrapper
