"""Server main runtime."""

from . import routes
from .app import app


for router in routes.ROUTERS:
    app.include_router(router)
