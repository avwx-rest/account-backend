"""
Server main runtime
"""

# pylint: disable=unused-import,import-error

from account import jwt, routes
from account.app import app


for router in routes.ROUTERS:
    app.include_router(router)


@app.get("/")
def root():
    return "Hello"
