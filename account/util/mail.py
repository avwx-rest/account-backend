"""
Mail server config
"""

from fastapi_mail import FastMail, ConnectionConfig, MessageSchema

from account.config import CONFIG

mail_conf = ConnectionConfig(
    MAIL_USERNAME=CONFIG.mail_username,
    MAIL_PASSWORD=CONFIG.mail_password,
    MAIL_FROM=CONFIG.mail_sender,
    MAIL_PORT=CONFIG.mail_port,
    MAIL_SERVER=CONFIG.mail_server,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
)

mail = FastMail(mail_conf)


VERIFY_TEMPLATE = """
Welcome to AVWX!

We just need to verify your email to begin.
Click the link below to continue.

{}
"""


RESET_TEMPLATE = """
Click the link to reset your AVWX account password:

{}

If you did not request this, please ignore this email
"""


async def send_verification_email(email: str, token: str):
    """Send user verification email"""
    # Change this later to public endpoint
    url = CONFIG.root_url + "/verify-email?t=" + token
    if CONFIG.mail_console:
        print("POST to " + url)
    else:
        message = MessageSchema(
            recipients=[email],
            subject="AVWX Email Verification",
            body=VERIFY_TEMPLATE.format(url),
        )
        await mail.send_message(message)


async def send_password_reset_email(email: str, token: str):
    """Sends password reset email"""
    # Change this later to public endpoint
    url = CONFIG.root_url + "/forgot-password?t=" + token
    if CONFIG.mail_console:
        print("POST to " + url)
    else:
        message = MessageSchema(
            recipients=[email],
            subject="AVWX Password Reset",
            body=RESET_TEMPLATE.format(url),
        )
        await mail.send_message(message)
