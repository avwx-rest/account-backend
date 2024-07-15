"""Server main runtime."""

from account import routes
from account.app import app
from account.config import CONFIG

for router in routes.ROUTERS:
    app.include_router(router)

if CONFIG.admin_root:
    from account.routes import admin

    app.include_router(admin.router)
