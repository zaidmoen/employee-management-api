from .settings import *  # noqa: F403


# Automated tests use a temporary database and never touch local MySQL data.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

