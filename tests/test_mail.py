"""Postmark mail sender tests."""

import json
from collections.abc import Iterator

import httpx
import pytest

from account.config import CONFIG
from account.util import mail


@pytest.fixture
def postmark_config() -> Iterator[None]:
    """Turn console mail off and set a Postmark token for the test."""
    console, token = CONFIG.mail_console, CONFIG.postmark_server_token
    CONFIG.mail_console = False
    CONFIG.postmark_server_token = "test-token"
    try:
        yield
    finally:
        CONFIG.mail_console, CONFIG.postmark_server_token = console, token


@pytest.mark.asyncio
@pytest.mark.usefixtures("postmark_config")
async def test_send_posts_to_postmark() -> None:
    """Test a message is posted to Postmark's email endpoint."""
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ErrorCode": 0, "Message": "OK"})

    await mail._send("user@test.io", "Subject", "Body", transport=httpx.MockTransport(handler))  # noqa: SLF001
    assert len(requests) == 1
    request = requests[0]
    assert str(request.url) == mail.POSTMARK_URL
    assert request.headers["X-Postmark-Server-Token"] == "test-token"
    payload = json.loads(request.content)
    assert payload == {
        "From": CONFIG.mail_sender,
        "To": "user@test.io",
        "Subject": "Subject",
        "TextBody": "Body",
        "MessageStream": CONFIG.postmark_message_stream,
    }


@pytest.mark.asyncio
@pytest.mark.usefixtures("postmark_config")
async def test_send_raises_on_rejection() -> None:
    """Test a rejected send raises with Postmark's reason."""

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"ErrorCode": 406, "Message": "Inactive recipient"})

    with pytest.raises(mail.MailError, match="HTTP 422"):
        await mail._send("user@test.io", "Subject", "Body", transport=httpx.MockTransport(handler))  # noqa: SLF001


@pytest.mark.asyncio
@pytest.mark.usefixtures("postmark_config")
async def test_send_raises_when_unreachable() -> None:
    """Test a network failure raises a mail error."""

    def handler(request: httpx.Request) -> httpx.Response:
        error = "down"
        raise httpx.ConnectError(error, request=request)

    with pytest.raises(mail.MailError, match="Could not reach Postmark"):
        await mail._send("user@test.io", "Subject", "Body", transport=httpx.MockTransport(handler))  # noqa: SLF001


@pytest.mark.asyncio
async def test_console_mail_skips_postmark(capsys: pytest.CaptureFixture[str]) -> None:
    """Test console mode prints the message instead of sending it."""
    console = CONFIG.mail_console
    CONFIG.mail_console = True
    try:
        await mail._send("user@test.io", "Subject", "Printed body")  # noqa: SLF001
    finally:
        CONFIG.mail_console = console
    assert "Printed body" in capsys.readouterr().out
