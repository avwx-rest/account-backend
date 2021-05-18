"""
User management routers
"""

from account.util.user_manager import manager

user = manager.get_users_router()
