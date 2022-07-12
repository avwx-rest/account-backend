"""
Server app config
"""

# pylint: disable=import-error

import rollbar
from rollbar.contrib.fastapi import ReporterMiddleware
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from mailchimp3 import MailChimp

from account import models
from account.config import CONFIG


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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def app_init():
    """Initialize application services"""
    # Init Database
    client = AsyncIOMotorClient(CONFIG.mongo_uri)
    app.db = client[CONFIG.database]
    documents = [
        models.addon.Addon,
        models.plan.Plan,
        models.token.TokenUsage,
        models.user.User,
    ]
    await init_beanie(app.db, document_models=documents)
    # Init error logging
    if CONFIG.log_key:
        rollbar.init(CONFIG.log_key, environment="production", handler="async")
        app.add_middleware(ReporterMiddleware)
    # Init mailing list
    if CONFIG.mc_key and CONFIG.mc_username:
        app.chimp = MailChimp(mc_api=CONFIG.mc_key, mc_user=CONFIG.mc_username)
    print("Startup complete")
