"""
Mail utilities
"""

import hashlib
from typing import Optional

import rollbar
from mailchimp3.mailchimpclient import MailChimpError

from account import app
from account.config import CONFIG


def add_to_mailing_list(email: str) -> Optional[str]:
    """Add an email to the mailing list. Returns error string if not successful"""
    try:
        data = {"email_address": email, "status": "subscribed"}
        app.mc.lists.members.create(CONFIG.MC_LIST_ID, data)
    except MailChimpError as exc:
        data = dict(exc.args[0])
        detail = data.get("detail")
        if detail and "fake or invalid" in detail:
            return "Your email looks suspicious. Email the admin to enable your account"
        if data.get("title") != "Member Exists":
            rollbar.report_message(data.update({"email": email}))
    except ConnectionError:
        return 'Something went wrong while adding you to the email list. If you wish to receive email updates, <a href="/subscribe">click here</a> to try again'
    return None


def delete_from_mailing_list(email: str):
    """Delete an email from the mailing list"""
    try:
        target = hashlib.md5(email.encode("utf-8")).hexdigest()
        app.mc.lists.members.delete(CONFIG.MC_LIST_ID, target)
    except MailChimpError as exc:
        data = dict(exc.args[0])
        if data.get("status") != 404:
            rollbar.report_message(data)
