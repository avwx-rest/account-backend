"""
App and global resources
"""

from fastapi import FastAPI
from montydb import MontyClient

app = FastAPI()
mdb = MontyClient(":memory:").db
