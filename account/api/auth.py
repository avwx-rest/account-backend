"""
Authentication management views
"""

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials

from account.app import app, mdb
from account.auth import AUTH, SECURITY
from account.models import AuthModel


@app.post("/signup")
def signup(user_details: AuthModel) -> str:
    user = mdb.users.find_one({"key": user_details.username})
    if user != None:
        return "Account already exists"
    try:
        hashed_password = AUTH.encode_password(user_details.password)
        user = {"key": user_details.username, "password": hashed_password}
        result = mdb.users.insert_one(user)
        return "Added"
    except:
        error_msg = "Failed to signup user"
        return error_msg


@app.post("/login")
def login(user_details: AuthModel):
    user = mdb.users.find_one({"key": user_details.username})
    if user is None:
        return HTTPException(status_code=401, detail="Invalid username")
    if not AUTH.verify_password(user_details.password, user["password"]):
        return HTTPException(status_code=401, detail="Invalid password")

    access_token = AUTH.encode_token(user["key"])
    refresh_token = AUTH.encode_refresh_token(user["key"])
    return {"access_token": access_token, "refresh_token": refresh_token}


@app.get("/refresh_token")
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(SECURITY)):
    refresh_token = credentials.credentials
    new_token = AUTH.refresh_token(refresh_token)
    return {"access_token": new_token}
