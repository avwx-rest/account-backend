"""Run nox test environment."""

import nox


@nox.session(python="3.12")
def tests(session: nox.Session) -> None:
    """Run test suite."""
    session.install(".")
    session.install(".[test]")
    session.run("pytest", "--disable-warnings")
