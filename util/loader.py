"""Import from this module before importing from account."""

# stdlib
import sys
from pathlib import Path

# library
from beanie import init_beanie, Document
from motor.motor_asyncio import AsyncIOMotorClient

sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

# module
from account.config import CONFIG  # noqa: E402


async def load_models(*model: Document) -> None:
    """Initialize beanie models."""
    db = AsyncIOMotorClient(CONFIG.mongo_uri).account
    await init_beanie(db, document_models=model)
