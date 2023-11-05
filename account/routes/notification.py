"""
Notification router
"""

# mypy: disable-error-code="no-untyped-def"

from fastapi import APIRouter, Depends, HTTPException, Response

from account.models.user import Notification, User
from account.util.current_user import current_user

router = APIRouter(prefix="/notification", tags=["Notification"])


@router.get("", response_model=list[Notification])
async def get_notifications(user: User = Depends(current_user)):
    """Returns the user's notifications"""
    return user.notifications


@router.delete("")
async def delete_notifications(user: User = Depends(current_user)):
    """Delete all the user's notifications"""
    user.notifications = []
    await user.save()
    return Response(status_code=204)


@router.delete("/{value}")
async def delete_notification(value: str, user: User = Depends(current_user)):
    """Deletes a single notification"""
    i, _ = user.get_notification(value)
    if i < 0:
        raise HTTPException(404, f"Notification with value {value} does not exist")
    user.notifications.pop(i)
    await user.save()
    return Response(status_code=204)
