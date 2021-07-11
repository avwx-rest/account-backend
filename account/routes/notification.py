"""
Notification router
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi_jwt_auth import AuthJWT

from account.models.user import Notification, User

router = APIRouter(prefix="/notification", tags=["Notification"])


@router.get("", response_model=list[Notification])
async def get_notifications(auth: AuthJWT = Depends()):
    """Returns the user's notifications"""
    auth.jwt_required()
    user = await User.by_email(auth.get_jwt_subject())
    return user.notifications


@router.delete("")
async def delete_notifications(auth: AuthJWT = Depends()):
    """Delete all the user's notifications"""
    auth.jwt_required()
    user = await User.by_email(auth.get_jwt_subject())
    user.notifications = []
    await user.save()
    return Response(status_code=204)


@router.delete("/{value}")
async def delete_notification(value: str, auth: AuthJWT = Depends()):
    """Deletes a single notification"""
    auth.jwt_required()
    user = await User.by_email(auth.get_jwt_subject())
    i, _ = user.get_notification(value)
    if i < 0:
        raise HTTPException(404, f"Notification with value {value} does not exist")
    user.notifications.pop(i)
    await user.save()
    return Response(status_code=204)
