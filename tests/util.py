"""
Common test utilities
"""

from httpx import AsyncClient


async def auth_headers(client: AsyncClient, email: str) -> dict[str, str]:
    """Returns the authorization headers for an email"""
    data = {"email": email, "password": email}
    resp = await client.post("/auth/login", json=data)
    return {"AUTHORIZATION": "Bearer " + resp.json()["access_token"]}
