"""
FastAPI server configuration
"""

# pylint: disable=too-few-public-methods

from decouple import config
from pydantic import BaseModel


class Settings(BaseModel):
    """Server config settings"""

    # Mongo Engine settings
    mongo_uri = config("MONGO_URI", default="mongodb://localhost:27017")
    database = "account"

    # Security settings
    authjwt_secret_key = config("SECRET_KEY")
    salt = config("SALT").encode()

    # FastMail SMTP server settings
    mail_console = config("MAIL_CONSOLE", default=False, cast=bool)
    mail_server = config("MAIL_SERVER", default="smtp.mailgun.org")
    mail_port = config("MAIL_PORT", default=587, cast=int)
    mail_username = config("MAIL_USERNAME", default="")
    mail_password = config("MAIL_PASSWORD", default="")
    mail_sender = config("MAIL_SENDER", default="noreply@avwx.rest")

    # Mailchimp Mailing List
    mc_key = config("MC_KEY", default="")
    mc_list_id = config("MC_LIST_ID", default="")
    mc_username = config("MC_USERNAME", default="")

    # Stripe Payments
    root_url = config("ROOT_URL", default="http://use.ngrok.for.this.locally")
    stripe_pub_key = config("STRIPE_PUB_KEY", default="")
    stripe_secret_key = config("STRIPE_SECRET_KEY", default="")
    stripe_sign_secret = config("STRIPE_SIGN_SECRET", default="")

    # Logging
    log_key = config("LOG_KEY", default="")

    # reCaptcha
    recaptcha_secret_key = config("RECAPTCHA_SECRET_KEY", default="")

    testing = config("TESTING", default=False, cast=bool)


CONFIG = Settings()
