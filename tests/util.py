"""
Common test utilities
"""

from httpx import AsyncClient

from account.models.auth import RefreshToken


async def auth_payload(
    client: AsyncClient, email: str, password: str = None
) -> RefreshToken:
    """Returns the login auth payload for an email"""
    data = {"email": email, "password": password or email}
    resp = await client.post("/auth/login", json=data)
    return RefreshToken(**resp.json())


async def auth_headers(
    client: AsyncClient, email: str, password: str = None
) -> dict[str, str]:
    """Returns the authorization headers for an email"""
    auth = await auth_payload(client, email, password)
    return {"AUTHORIZATION": "Bearer " + auth.access_token}
