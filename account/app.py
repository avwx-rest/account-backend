"""
Server app config
"""

# pylint: disable=import-error

from fastapi import FastAPI
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from account.config import CONFIG
from account.models.addon import Addon
from account.models.plan import Plan
from account.models.token import TokenUsage
from account.models.user import User


DESCRIPTION = """
This API powers the account management portal

It supports:

- Account sign-up and management
- API token management and usage history
- API plan and Stripe subscription assignment
"""


app = FastAPI(
    title="AVWX Account API",
    description=DESCRIPTION,
    version="0.0.1",
    contact={
        "name": "Michael duPont",
        "url": "https://avwx.rest",
        "email": "michael@dupont.dev",
    },
    license_info={
        "name": "MIT",
        "url": "https://github.com/avwx-rest/account-backend/blob/main/LICENSE",
    },
)


@app.on_event("startup")
async def app_init():
    """Initialize application services"""
    app.db = AsyncIOMotorClient(CONFIG.mongo_uri).account
    await init_beanie(app.db, document_models=[Addon, Plan, TokenUsage, User])


# Rollbar error logging middleware
if CONFIG.log_key:
    import rollbar
    from rollbar.contrib.fastapi import ReporterMiddleware

    rollbar.init(
        CONFIG.log_key, "avwx_account", environment="production", handler="async"
    )
    app.add_middleware(ReporterMiddleware)
