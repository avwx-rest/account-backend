"""
App and global resources
"""

from fastapi import FastAPI
from montydb import MontyClient

app = FastAPI()
app.db = MontyClient(":memory:").account


@app.on_event("shutdown")
async def shutdown_event():
    app.db.close()
