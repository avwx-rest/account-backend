"""
reCaptcha verification
"""

from httpx import AsyncClient
from account.config import CONFIG


THRESHOLD = 0.6
TIMEOUT = 10
URL = "https://www.google.com/recaptcha/api/siteverify"


async def verify(token: str) -> bool:
    """Call reCaptcha service to verify data token"""
    if CONFIG.testing:
        return True
    async with AsyncClient(timeout=10) as client:
        resp = await client.post(
            URL,
            params={
                "response": token,
                "secret": CONFIG.recaptcha_secret_key,
            },
        )
    data = resp.json()
    if data.get("success") is not True:
        return False
    score = data.get("score")
    return isinstance(score, float) and score >= THRESHOLD
