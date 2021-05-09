"""
Root views
"""

from account.app import app
from account.auth import auth_required


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/secret")
@auth_required
async def secret_data():
    return "Top Secret data only authorized users can access this info"


@app.get("/notsecret")
async def not_secret_data():
    return "Not secret data"
