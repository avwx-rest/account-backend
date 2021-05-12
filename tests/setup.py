"""
"""

from fastapi import FastAPI
from montydb import MontyClient

from account.auth import AUTH

# def add_test_users

def set_test_database(app: FastAPI, test_data: bool = True) -> FastAPI:
    """Replace the MongoClient with an in-memory test client"""
    app.db = MontyClient(":memory:").account
    if test_data:
        hashed_password = AUTH.encode_password("testing1")
        app.db.users.insert_one({"username": "test1", "password": hashed_password})

def get_test_app(test_data: bool = True) -> FastAPI:
    """"""
    from account.main import app
    return set_test_database(app, test_data)
