import nox


@nox.session(python="3.10")
def tests(session):
    session.install("-r", "requirements.txt")
    session.install("-r", "tests/requirements.txt")
    session.run("pytest", "--disable-warnings")
