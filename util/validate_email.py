"""
Verify a user's email
"""


# stdlib
from datetime import datetime
from os import environ

# library
import typer
from datetime import timezone
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def validate_email(email: str) -> int:
    """Force validates a user's email"""
    mdb = MongoClient(environ["MONGO_URI"])
    command = {"$set": {"email_confirmed_at": datetime.now(timezone.utc)}}
    resp = mdb.account.user.update_one({"email": email}, command)
    if not resp.matched_count:
        print(f"No user found for {email}")
    elif not resp.modified_count:
        print(f"{email} is already verified")
    else:
        print(f"{email} has been verified")
        return 0
    return 2


if __name__ == "__main__":
    typer.run(validate_email)
