"""
Generate email reset link
"""

from os import environ
import typer
from dotenv import load_dotenv
from fastapi_jwt_auth import AuthJWT

load_dotenv()

def get_reset_link(email: str):
    auth = AuthJWT()
    auth._secret_key = environ["SECRET_KEY"]
    token = auth.create_access_token(email, expires_time=24*60*60)
    url = f"https://account.avwx.rest/forgot-password?t={token}"
    print(url)


if __name__ == "__main__":
    typer.run(get_reset_link)
