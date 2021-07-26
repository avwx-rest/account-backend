"""
Token management router
"""

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Response

from account.models.token import Token, TokenUpdate, TokenUsage, TokenUsageOut
from account.models.user import User, UserToken
from account.util.current_user import current_user

router = APIRouter(prefix="/token", tags=["Token"])


@router.get("", response_model=list[Token])
async def get_user_tokens(user: User = Depends(current_user)):
    """Returns the current user's tokens"""
    return user.tokens


@router.post("", response_model=Token)
async def new_token(user: User = Depends(current_user)):
    """Creates a new user token"""
    token = await UserToken.new()
    user.tokens.append(token)
    await user.save()
    return token


@router.get("/{value}", response_model=Token)
async def get_token(value: str, user: User = Depends(current_user)):
    """Returns token details by string value"""
    _, token = user.get_token(value)
    if token is None:
        raise HTTPException(404, f"Token with value {value} does not exist")
    return token


@router.patch("/{value}", response_model=Token)
async def update_token(
    value: str, update: TokenUpdate, user: User = Depends(current_user)
):
    """Updates token details by string value"""
    i, token = user.get_token(value)
    if token is None:
        raise HTTPException(404, f"Token with value {value} does not exist")
    token = token.copy(update=update.dict(exclude_unset=True))
    user.tokens[i] = token
    await user.save()
    return token


@router.delete("/{value}", response_model=Token)
async def delete_token(value: str, user: User = Depends(current_user)):
    """Deletes a token by string value"""
    i, token = user.get_token(value)
    if token is None:
        raise HTTPException(404, f"Token with value {value} does not exist")
    user.tokens.pop(i)
    await user.save()
    return Response(status_code=204)


@router.post("/{value}/refresh", response_model=Token)
async def refresh_token(value: str, user: User = Depends(current_user)):
    """Refreshes token value by string value"""
    i, token = user.get_token(value)
    if token is None:
        raise HTTPException(404, f"Token with value {value} does not exist")
    await user.tokens[i].refresh()
    await user.save()
    return user.tokens[i]


@router.get("/{value}/history", response_model=list[TokenUsageOut])
async def get_token_history(value: str, user: User = Depends(current_user)):
    """Return a token's usage history"""
    _, token = user.get_token(value)
    return await TokenUsage.find(TokenUsage.token_id == ObjectId(token.id)).to_list()
