"""FastAPI server configuration."""

from decouple import config
from pydantic import BaseModel


class Settings(BaseModel):
    """Server config settings."""

    # Mongo Engine settings
    mongo_uri: str = config("MONGO_URI", default="mongodb://localhost:27017")
    database: str = "account"

    # Security settings
    authjwt_secret_key: str = config("SECRET_KEY")
    salt: bytes = config("SALT").encode()

    # Postmark transactional email
    mail_console: bool = config("MAIL_CONSOLE", default=False, cast=bool)
    mail_sender: str = config("MAIL_SENDER", default="AVWX <noreply@avwx.rest>")
    postmark_server_token: str = config("POSTMARK_SERVER_TOKEN", default="")
    postmark_message_stream: str = config("POSTMARK_MESSAGE_STREAM", default="outbound")

    # Mailchimp Mailing List
    mc_key: str = config("MC_KEY", default="")
    mc_list_id: str = config("MC_LIST_ID", default="")
    mc_username: str = config("MC_USERNAME", default="")

    # Stripe Payments
    root_url: str = config("ROOT_URL", default="http://use.ngrok.for.this.locally")
    stripe_pub_key: str = config("STRIPE_PUB_KEY", default="")
    stripe_secret_key: str = config("STRIPE_SECRET_KEY", default="")
    stripe_sign_secret: str = config("STRIPE_SIGN_SECRET", default="")

    # Logging
    log_key: str = config("LOG_KEY", default="")

    # reCaptcha
    recaptcha_secret_key: str = config("RECAPTCHA_SECRET_KEY", default="")

    admin_root: str = config("ADMIN_ROOT", default="")
    testing: bool = config("TESTING", default=False, cast=bool)


CONFIG = Settings()
