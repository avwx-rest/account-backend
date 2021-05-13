"""
"""

from os import environ
from dotenv import load_dotenv

load_dotenv()


class APPConfig:

    # Mongo Engine settings
    MONGO_URI = "mongodb://localhost:27017/account"

    # Security settings
    SECRET_KEY = "change my secret key"

    # FastMail SMTP server settings
    MAIL_SERVER = "smtp.mailgun.org"
    MAIL_PORT = 587
    MAIL_USERNAME = "mail username"
    MAIL_PASSWORD = "mail password"
    MAIL_SENDER = "noreply@avwx.rest"

    # Mailchimp Mailing List
    MC_KEY = "mc api key"
    MC_LIST_ID = "mc mailing list"
    MC_USERNAME = "mc username"

    # Stripe Payments
    ROOT_URL = "http://use.ngrok.for.this.locally/"
    STRIPE_PUB_KEY = "stripe public key"
    STRIPE_SECRET_KEY = "stripe secret key"
    STRIPE_SIGN_SECRET = "stripe webhook signing key"

    def __init__(self) -> None:
        for key in ("MONGO_URI", "SECRET_KEY", "MAIL_USERNAME", "MAIL_PASSWORD"):
            if value := environ.get(key):
                setattr(self, key, value)


CONFIG = APPConfig()
