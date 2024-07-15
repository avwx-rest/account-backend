"""Admin routes."""

from fastapi import APIRouter

from account.config import CONFIG
from account.routes.admin import stripe, token, user

router = APIRouter(prefix=f"/{CONFIG.admin_root}", include_in_schema=False)

router.include_router(stripe.router)
router.include_router(token.router)
router.include_router(user.router)
