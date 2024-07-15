# account-backend

[![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AVWX account management backend service


## Intro

The AVWX Account API runs on top of a [MongoDB]() store with the following features:

- Registration
- Email verification
- Password reset
- JWT auth login and refresh
- User model CRUD
- Token management and usage
- Stripe Checkout integration

It's built on top of these libraries to provide those features:

- [FastAPI]() - Python async micro framework built on [Starlette]() and [PyDantic]()
- [Beanie ODM]() - Async [MongoDB]() object-document mapper built on [PyDantic]()
- [fastapi-jwt]() - JWT auth for [FastAPI]()
- [fastapi-mail]() - Mail server manager for [FastAPI]()

## Setup

This codebase was written for Python 3.12 and above. Don't forget about a venv as well. The `python` commands below assume you're pointing to your desired Python3 target.

We use [hatch]() to manage all of our tooling and sub-environments, but you may still wish to install the requirements if you want things like autocomplete to work in your code editor of choice.

```bash
python -m pip install -e .
```

Before we run the server, there is one config variable you'll need to generate: the password salt. To do this, just run the script in this repo.

```bash
cp sample.env .env
python util/gen_salt.py
```

There are other settings in `config.py` and the included `.env` file. Assuming you've changed the SALT value, everything should be able to test as-is if there is a local [MongoDB]() instance running ([see below](#test) for a Docker solution). Certain runtime features are disabled during testing. You will need to fill in the Stripe fields before the server is fully operational. Any email links will be printed to the console by default.

## Run

The API uses [uvicorn]() as our ASGI web server. This allows us to run our server code in a much more robust and configurable environment than the development server. For example, ASGI servers let you run multiple workers that recycle themselves after a set amount of time or number of requests.

```bash
hatch run serve:reload
```

Your API should now be available at http://localhost:8080

You can also let Docker manage the Python runtime if you want to. Just make sure you found a way to set the salt in the environment variables.

```bash
docker build -t avwx-account .
docker run -p 8080:8080 avwx-account
```

## Develop

This codebase is uses [mypy]() for type checking and [hatch]() for everything else.

To run the type checker:

```bash
hatch run types:check
```

To run the linter and code formatter:

```bash
hatch fmt
```

## Test

The tests need access to a [MongoDB]() store that is emptied at the end of each test. The easiest way to do this is to run a Mongo container in the background.

```bash
docker run -d -p 27017:27017 mongo:7
```

You can also connect to a remote server if you're running tests in a CI/CD pipeline. Just set the `TEST_MONGO_URI` in the environment. This value defaults to localhost and is only checked in the test suite. It should **never** use your `MONGO_URI`.

Then just run the test suite.

```bash
hatch test
```

[MongoDB]: https://www.mongodb.com "MongoDB NoSQL homepage"
[FastAPI]: https://fastapi.tiangolo.com "FastAPI web framework"
[Beanie ODM]: https://roman-right.github.io/beanie/ "Beanie object-document mapper"
[Starlette]: https://www.starlette.io "Starlette web framework"
[PyDantic]: https://pydantic-docs.helpmanual.io "PyDantic model validation"
[fastapi-jwt]: https://github.com/k4black/fastapi-jwt "JWT auth for FastAPI"
[fastapi-mail]: https://github.com/sabuhish/fastapi-mail "FastAPI mail server"
[uvicorn]: https://www.uvicorn.org "Uvicorn ASGI web server"
[mypy]: https://www.mypy-lang.org "mypy Python type checker"
[hatch]: https://hatch.pypa.io/latest/ "Hatch project and tooling manager"