from .settings import *  # noqa: F403


# A file-backed SQLite database is shared by Django and SQLAlchemy connections.
# Django removes it after the test run, and it never touches local MySQL data.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "/tmp/employee-management-api-tests.sqlite3",
        "TEST": {"NAME": "/tmp/employee-management-api-tests.sqlite3"},
    }
}
