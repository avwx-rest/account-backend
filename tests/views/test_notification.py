"""
Notification management tests
"""

import pytest
from httpx import AsyncClient

from tests.data import add_notification_user
from tests.util import auth_headers


@pytest.mark.asyncio
async def test_get_notifications(client: AsyncClient) -> None:
    """Test notification endpoint returns all user notifications"""
    text = ("Thank you", "Testing")
    email = await add_notification_user(*text)
    auth = await auth_headers(client, email)
    resp = await client.get("/notification", headers=auth)
    assert resp.status_code == 200
    notifications = resp.json()
    assert len(notifications) == len(text)
    for value, notification in zip(text, notifications):
        assert notification["type"] == "app"
        assert notification["text"] == value
        assert "timestamp" in notification
        assert "id" in notification


@pytest.mark.asyncio
async def test_delete_notifications(client: AsyncClient) -> None:
    """Test deleting all user notifications"""
    text = ("Thank you", "Testing")
    email = await add_notification_user(*text)
    auth = await auth_headers(client, email)
    resp = await client.get("/notification", headers=auth)
    assert resp.status_code == 200
    assert len(resp.json()) == len(text)
    resp = await client.delete("/notification", headers=auth)
    assert resp.status_code == 204
    resp = await client.get("/notification", headers=auth)
    assert resp.status_code == 200
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_delete_notification(client: AsyncClient) -> None:
    """Test deleting a single user notifications"""
    text = ("Thank you", "Testing")
    email = await add_notification_user(*text)
    auth = await auth_headers(client, email)
    resp = await client.get("/notification", headers=auth)
    assert resp.status_code == 200
    notifications = resp.json()
    assert len(notifications) == len(text)
    value = notifications[0]["id"]
    resp = await client.delete("/notification/" + value, headers=auth)
    assert resp.status_code == 204
    resp = await client.get("/notification", headers=auth)
    assert resp.status_code == 200
    notifications = resp.json()
    assert len(notifications) == len(text) - 1
    for notification in notifications:
        assert notification["id"] != value
