"""Other output models."""

from pydantic import BaseModel


class JustUrl(BaseModel):
    """Just returns a URL."""

    url: str
