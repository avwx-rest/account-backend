"""Server main runtime."""

from . import routes
from .app import app
from .config import CONFIG


for router in routes.ROUTERS:
    app.include_router(router)

if CONFIG.admin_root:
    from .routes import admin

    app.include_router(admin.router)
