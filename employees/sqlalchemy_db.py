"""SQLAlchemy session setup for the phase 3 shift workflow."""

from django.conf import settings
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker


def _database_url():
    database = settings.DATABASES["default"]
    if database["ENGINE"].endswith("sqlite3"):
        return URL.create("sqlite", database=database["NAME"])
    return URL.create(
        "mysql+pymysql",
        username=database.get("USER") or None,
        password=database.get("PASSWORD") or None,
        host=database.get("HOST") or "127.0.0.1",
        port=int(database.get("PORT") or 3306),
        database=database["NAME"],
        query={"charset": "utf8mb4"},
    )


engine = create_engine(_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
