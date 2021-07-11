"""
Token management router
"""

from fastapi import APIRouter, Depends, Response
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT

from account.models.token import Token, TokenUpdate, TokenUsage, TokenUsageOut
from account.models.user import User, UserToken

router = APIRouter(prefix="/token", tags=["Token"])


@router.get("", response_model=list[Token])
async def get_user_tokens(auth: AuthJWT = Depends()):
    """Returns the current user's tokens"""
    auth.jwt_required()
    user = await User.by_email(auth.get_jwt_subject())
    return user.tokens


@router.post("", response_model=Token)
async def new_token(auth: AuthJWT = Depends()):
    """Creates a new user token"""
    auth.jwt_required()
    user = await User.by_email(auth.get_jwt_subject())
    token = await UserToken.new()
    user.tokens.append(token)
    await user.save()
    return token


@router.get("/{value}", response_model=Token)
async def get_token(value: str, auth: AuthJWT = Depends()):
    """Returns token details by string value"""
    auth.jwt_required()
    user = await User.by_email(auth.get_jwt_subject())
    _, token = user.get_token(value)
    if token is None:
        raise HTTPException(404, f"Token with value {value} does not exist")
    return token


@router.patch("/{value}", response_model=Token)
async def update_token(value: str, update: TokenUpdate, auth: AuthJWT = Depends()):
    """Updates token details by string value"""
    auth.jwt_required()
    user = await User.by_email(auth.get_jwt_subject())
    i, token = user.get_token(value)
    if token is None:
        raise HTTPException(404, f"Token with value {value} does not exist")
    token = token.copy(update=update.dict(exclude_unset=True))
    user.tokens[i] = token
    await user.save()
    return token


@router.delete("/{value}", response_model=Token)
async def delete_token(value: str, auth: AuthJWT = Depends()):
    """Deletes a token by string value"""
    auth.jwt_required()
    user = await User.by_email(auth.get_jwt_subject())
    i, token = user.get_token(value)
    if token is None:
        raise HTTPException(404, f"Token with value {value} does not exist")
    user.tokens.pop(i)
    await user.save()
    return Response(status_code=204)


@router.post("/{value}/refresh", response_model=Token)
async def refresh_token(value: str, auth: AuthJWT = Depends()):
    """Refreshes token value by string value"""
    auth.jwt_required()
    user = await User.by_email(auth.get_jwt_subject())
    i, token = user.get_token(value)
    if token is None:
        raise HTTPException(404, f"Token with value {value} does not exist")
    await user.tokens[i].refresh()
    await user.save()
    return user.tokens[i]


@router.get("/{value}/history", response_model=list[TokenUsageOut])
async def get_token_history(value: str, auth: AuthJWT = Depends()):
    """Return a token's usage history"""
    auth.jwt_required()
    user = await User.by_email(auth.get_jwt_subject())
    _, token = user.get_token(value)
    return await TokenUsage.find(TokenUsage.token_id == token.id).to_list()
