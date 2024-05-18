"""Test main with logfire tracing."""

import logfire
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor


logfire.configure(pydantic_plugin=logfire.PydanticPlugin(record="all"))
logfire.install_auto_tracing(modules=["account"])
PymongoInstrumentor().instrument(capture_statement=True)

from account.main import app  # noqa: E402


logfire.instrument_fastapi(app)
