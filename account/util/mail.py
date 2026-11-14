"""Transactional email, sent through Postmark's email API."""

from typing import Final

import httpx

from account.config import CONFIG

POSTMARK_URL: Final = "https://api.postmarkapp.com/email"
TIMEOUT_SECONDS: Final = 10.0
# Enough of Postmark's own error message to diagnose a failure, not a whole page
_ERROR_BODY_LIMIT: Final = 500


class MailError(RuntimeError):
    """A send was attempted and Postmark did not accept it."""


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

CHANGE_EMAIL_OLD = "Your AVWX account email has been changed to {}. If you did not make this change, please contact avwx@dupont.dev immediately."
CHANGE_EMAIL_NEW = "Your AVWX account email has been changed. No further action is needed."


async def _send(email: str, title: str, msg: str, *, transport: httpx.AsyncBaseTransport | None = None) -> None:
    """Send to email or print to console."""
    if CONFIG.mail_console:
        print(msg)
        return
    payload = {
        "From": CONFIG.mail_sender,
        "To": email,
        "Subject": title,
        "TextBody": msg,
        "MessageStream": CONFIG.postmark_message_stream,
    }
    headers = {
        "Accept": "application/json",
        "X-Postmark-Server-Token": CONFIG.postmark_server_token,
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, transport=transport) as client:
            response = await client.post(POSTMARK_URL, json=payload, headers=headers)
    except httpx.HTTPError as exc:
        error = f"Could not reach Postmark: {exc}"
        raise MailError(error) from exc
    if response.status_code != httpx.codes.OK:
        error = f"Postmark rejected the message with HTTP {response.status_code}: {response.text[:_ERROR_BODY_LIMIT]}"
        raise MailError(error)


async def send_verification_email(email: str, token: str) -> None:
    """Send user verification email."""
    # Change this later to public endpoint
    url = f"{CONFIG.root_url}/verify-email?t={token}"
    await _send(email, "AVWX Email Verification", VERIFY_TEMPLATE.format(url))


async def send_password_reset_email(email: str, token: str) -> None:
    """Send password reset email."""
    # Change this later to public endpoint
    url = f"{CONFIG.root_url}/forgot-password?t={token}"
    await _send(email, "AVWX Password Reset", RESET_TEMPLATE.format(url))


async def send_disable_email(email: str, portal_url: str, *, warning: bool = False) -> None:
    """Send missed payment email with portal link."""
    title = "AVWX Account "
    if warning:
        title += "Payment"
        template = ACCOUNT_WARNING
    else:
        title += "Disabled"
        template = ACCOUNT_DISABLE
    await _send(email, title, template.format(portal_url))


async def send_enabled_email(email: str) -> None:
    """Send account re-enabled status email."""
    await _send(email, "AVWX Account Re-Enabled", ACCOUNT_ENABLE)


async def send_email_change(old: str, new: str) -> None:
    """Send email chnage to old and new address."""
    title = "AVWX Change Passord"
    await _send(old, title, CHANGE_EMAIL_OLD.format(new))
    await _send(new, title, CHANGE_EMAIL_NEW)
