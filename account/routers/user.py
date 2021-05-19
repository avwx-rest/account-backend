"""
User management routers
"""

from account.util.user_manager import manager

current_user = manager.get_users_router()

# Remove user-by-ID ops
_remove = ("get_user", "update_user", "delete_user")
for i, route in reversed(list(enumerate(current_user.routes))):
    if route.name in _remove:
        current_user.routes.pop(i)
