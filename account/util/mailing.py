"""Mailing list manager."""

import hashlib

import rollbar
from kewkew import Kew
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError

from account.config import CONFIG
from account.models.user import User


class MailingKew(Kew):
    """Mailing list queue manager."""

    async def worker(self, data: tuple[User, bool]) -> bool:
        """Queue worker to add/remove subscriber and update."""
        match data:
            case (user, True | False as add):
                handler = _add_to_mailing if add else _remove_from_mailing
                if handler(user.email):
                    user.subscribed = add
                    await user.save()
            case (old, new) if isinstance(old, str) and isinstance(new, str):
                _update_mailing(old, new)
        return True


if not CONFIG.testing:
    kew = MailingKew()
    if CONFIG.mc_key and CONFIG.mc_username:
        chimp = MailChimp(mc_api=CONFIG.mc_key, mc_user=CONFIG.mc_username)


NOT_FOUND = 404


async def add_to_mailing(user: User) -> None:
    """Add an email to the mailing list."""
    if not CONFIG.testing:
        await kew.add((user, True))
    user.subscribed = True


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
    """Delete an email from the mailing list."""
    if not CONFIG.testing:
        await kew.add((user, False))
    user.subscribed = False


def _remove_from_mailing(email: str) -> bool:
    try:
        target = hashlib.md5(email.encode("utf-8")).hexdigest()  # noqa S324
        chimp.lists.members.delete(CONFIG.mc_list_id, target)
    except MailChimpError as exc:
        data = dict(exc.args[0])
        if data.get("status") != NOT_FOUND:
            rollbar.report_message(data)
    return True


async def update_mailing(old: str, new: str) -> None:
    """Update an email on the mailing list."""
    if not CONFIG.testing:
        await kew.add((old, new))


def _update_mailing(old: str, new: str) -> None:
    try:
        target = hashlib.md5(old.encode("utf-8")).hexdigest()  # noqa S324
        chimp.lists.members.update(
            CONFIG.mc_list_id,
            target,
            {"email_address": new},
        )
    except MailChimpError as exc:
        data = dict(exc.args[0])
        if data.get("status") != NOT_FOUND:
            rollbar.report_message(data)
