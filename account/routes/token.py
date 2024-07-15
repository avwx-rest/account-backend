"""Token management router."""

from datetime import UTC, datetime, timedelta

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Response

from account.models.token import (
    AllTokenUsageOut,
    Token,
    TokenUpdate,
    TokenUsage,
    TokenUsageOut,
)
from account.models.user import User, UserToken
from account.util.current_user import current_user
from account.util.token import token_usage_for

router = APIRouter(prefix="/token", tags=["Token"])


@router.get("", response_model=list[Token])
async def get_user_tokens(user: User = Depends(current_user)) -> list[UserToken]:
    """Return the current user's tokens."""
    return user.tokens


@router.post("", response_model=Token)
async def new_token(user: User = Depends(current_user)) -> UserToken:
    """Create a new user token."""
    token = await UserToken.new()
    user.tokens.append(token)
    await user.save()
    return token


@router.get("/history")
async def get_all_history(days: int = 30, user: User = Depends(current_user)) -> list[AllTokenUsageOut]:
    """Return all recent token history."""
    return await token_usage_for(user, days)


@router.get("/{value}", response_model=Token)
async def get_token(value: str, user: User = Depends(current_user)) -> UserToken:
    """Return token details by string value."""
    _, token = user.get_token(value)
    if token is None:
        raise HTTPException(404, f"Token with value {value} does not exist")
    return token


@router.patch("/{value}", response_model=Token)
async def update_token(value: str, update: TokenUpdate, user: User = Depends(current_user)) -> UserToken:
    """Update token details by string value."""
    i, token = user.get_token(value)
    if token is None:
        raise HTTPException(404, f"Token with value {value} does not exist")
    token = token.model_copy(update=update.model_dump(exclude_unset=True))
    user.tokens[i] = token
    await user.save()
    return token


@router.delete("/{value}")
async def delete_token(value: str, user: User = Depends(current_user)) -> Response:
    """Delete a token by string value."""
    i, token = user.get_token(value)
    if token is None:
        raise HTTPException(404, f"Token with value {value} does not exist")
    user.tokens.pop(i)
    await user.save()
    return Response(status_code=204)


@router.post("/{value}/refresh", response_model=Token)
async def refresh_token(value: str, user: User = Depends(current_user)) -> UserToken:
    """Refresh token value by string value."""
    i, token = user.get_token(value)
    if token is None:
        raise HTTPException(404, f"Token with value {value} does not exist")
    await user.tokens[i].refresh()
    await user.save()
    return user.tokens[i]


@router.get("/{value}/history", response_model=list[TokenUsageOut])
async def get_token_history(value: str, days: int = 30, user: User = Depends(current_user)) -> list[TokenUsage]:
    """Return a token's usage history."""
    _, token = user.get_token(value)
    if token is None:
        raise HTTPException(404, f"Token with value {value} does not exist")
    days_since = datetime.now(tz=UTC) - timedelta(days=days)
    return await TokenUsage.find(TokenUsage.token_id == ObjectId(token.id), TokenUsage.date >= days_since).to_list()
