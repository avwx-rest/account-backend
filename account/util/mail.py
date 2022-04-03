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

ACCOUNT_WARNING = """
It appears there was an issue processing your recent invoice. Use the link below to update your billing information:

{}

If the second attempt fails, your account will be temporarily disabled and block access to the API.
"""

ACCOUNT_DISABLE = """
Your account has been disabled after two failed attempts, and your account tokens have been temporarily blocked. Use the link below to update your billing info to resume service:

{}
"""

ACCOUNT_ENABLE = "Just letting you know that your account has been re-enabled and your API tokens activated. No further action is required."


async def _send(email: str, title: str, msg: str) -> None:
    """Send to email or print to console"""
    if CONFIG.mail_console:
        print(msg)
    else:
        message = MessageSchema(
            recipients=[email],
            subject=title,
            body=msg,
        )
        await mail.send_message(message)


async def send_verification_email(email: str, token: str) -> None:
    """Send user verification email"""
    # Change this later to public endpoint
    url = CONFIG.root_url + "/verify-email?t=" + token
    await _send(email, "AVWX Email Verification", VERIFY_TEMPLATE.format(url))


async def send_password_reset_email(email: str, token: str) -> None:
    """Sends password reset email"""
    # Change this later to public endpoint
    url = CONFIG.root_url + "/forgot-password?t=" + token
    await _send(email, "AVWX Password Reset", RESET_TEMPLATE.format(url))


async def send_disable_email(
    email: str, portal_url: str, warning: bool = False
) -> None:
    """Sends missed payment email with portal link"""
    title = "AVWX Account "
    if warning:
        title += "Payment"
        template = ACCOUNT_WARNING
    else:
        title += "Disabled"
        template = ACCOUNT_DISABLE
    await _send(email, title, template.format(portal_url))


async def send_enabled_email(email: str) -> None:
    """Sends account re-enabled status email"""
    await _send(email, "AVWX Account Re-Enabled", ACCOUNT_ENABLE)
