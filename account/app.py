"""
Server app config
"""

# pylint: disable=import-error

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from account.config import CONFIG
from account.models.addon import Addon
from account.models.plan import Plan
from account.models.user import User

app = FastAPI()
app.db = AsyncIOMotorClient(CONFIG.mongo_uri).account


@app.on_event("startup")
async def app_init():
    """Initialize application services"""
    await init_beanie(app.db, document_models=[Addon, Plan, User])
