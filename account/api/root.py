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
async def secret_data(email: str):
    return f"Top Secret data that only {email} can access"


@app.get("/notsecret")
async def not_secret_data():
    return "Not secret data"
