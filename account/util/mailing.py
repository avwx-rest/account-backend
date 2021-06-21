"""
Mailing list manager
"""

import hashlib
from typing import Tuple

import rollbar
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError
from kewkew import Kew

from account.config import CONFIG
from account.models.user import User


chimp = MailChimp(mc_api=CONFIG.mc_key, mc_user=CONFIG.mc_username)


class MailingKew(Kew):
    """Mailing list queue manager"""

    async def worker(self, data: Tuple[User, bool]) -> bool:
        """Queue worker to add/remove subscriber and update"""
        user, add = data
        handler = _add_to_mailing if add else _remove_from_mailing
        if handler(user.email):
            user.subscribed = add
            await user.save()
        return True


kew = MailingKew()


async def add_to_mailing(user: User) -> bool:
    """Add an email to the mailing list"""
    await kew.add((user, True))


def _add_to_mailing(email: str) -> bool:
    try:
        chimp.lists.members.create(
            CONFIG.mc_list_id,
            {"email_address": email, "status": "subscribed"},
        )
    except MailChimpError as exc:
        data = dict(exc.args[0])
        detail = data.get("detail")
        if detail and "fake or invalid" in detail:
            return False
        if data.get("title") != "Member Exists":
            rollbar.report_message(data.update({"email": email}))
    except ConnectionError:
        return False
    return True


async def remove_from_mailing(user: User) -> None:
    """Delete an email from the mailing list"""
    await kew.add((user, False))


def _remove_from_mailing(email: str) -> bool:
    try:
        target = hashlib.md5(email.encode("utf-8")).hexdigest()
        chimp.lists.members.delete(CONFIG.mc_list_id, target)
    except MailChimpError as exc:
        data = dict(exc.args[0])
        if data.get("status") != 404:
            rollbar.report_message(data)
    return True
