"""Token admin routes."""

from fastapi import APIRouter, Depends

from account.models.token import AllTokenUsageOut
from account.models.user import User
from account.util.current_user import admin_user, embedded_user
from account.util.token import token_usage_for

router = APIRouter(prefix="/token")


@router.post("/history", dependencies=[Depends(admin_user)])
async def get_all_history(days: int = 30, user: User = Depends(embedded_user)) -> list[AllTokenUsageOut]:
    """Return all recent token history for another user."""
    return await token_usage_for(user, days)
