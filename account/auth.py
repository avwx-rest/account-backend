"""
Authentication Manager
"""

# Initial implementation from:
# https://github.com/rohanshiva/Deta-FastAPI-JWT-Auth-Blog

# stdlib
import inspect
import os
from datetime import datetime, timedelta

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

    def encode_token(self, email: str) -> bytes:
        now = datetime.utcnow()
        payload = {
            "exp": now + timedelta(days=0, minutes=30),
            "iat": now,
            "scope": "access_token",
            "sub": email,
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def decode_token(self, token: str) -> str:
        """Returns the email associated with the token if valid"""
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
                email = payload["sub"]
                new_token = self.encode_token(email)
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
        if email := AUTH.decode_token(token):
            return await handler(email, *args, **kwargs)

    # Fix signature of wrapper
    # for func in (handler, wrapper):
    #     print(inspect.signature(func).parameters.items())

    exempt = (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)

    wrapper.__signature__ = inspect.Signature(
        parameters=[
            # Use all parameters from handler except added email from token
            *[
                v
                for k, v in inspect.signature(handler).parameters.items()
                if k != "email"
            ],
            # Skip *args and **kwargs from wrapper parameters:
            *[
                v
                for v in inspect.signature(wrapper).parameters.values()
                if v.kind not in exempt
            ],
        ],
        return_annotation=inspect.signature(handler).return_annotation,
    )

    return wrapper
