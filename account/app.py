"""Server app config."""

from contextlib import asynccontextmanager

import logfire
import rollbar
from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from rollbar.contrib.fastapi import ReporterMiddleware
from starlette.middleware.cors import CORSMiddleware

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


@asynccontextmanager
@logfire.no_auto_trace
async def lifespan(app: FastAPI):  # type: ignore
    """Initialize application services."""
    # Init Database
    client: AsyncIOMotorClient = AsyncIOMotorClient(CONFIG.mongo_uri.strip('"'))
    app.state.db = client[CONFIG.database]
    documents = [Addon, Plan, TokenUsage, User]
    await init_beanie(app.state.db, document_models=documents)  # type: ignore
    print("Startup complete")
    yield
    print("Shutdown complete")


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
    lifespan=lifespan,
)

# Init error logging
if CONFIG.log_key:
    rollbar.init(CONFIG.log_key, environment="production", handler="async")
    app.add_middleware(ReporterMiddleware)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
