"""SQLAlchemy connection used by employee API repositories."""
import os
from contextlib import contextmanager

from django.conf import settings
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def database_url():
    override = os.getenv("SQLALCHEMY_DATABASE_URL")
    if override:
        return override
    db = settings.DATABASES["default"]
    if db["ENGINE"] == "django.db.backends.sqlite3":
        return f"sqlite:///{db['NAME']}"
    return URL.create(
        "mysql+pymysql", username=db["USER"], password=db["PASSWORD"],
        host=db["HOST"], port=int(db["PORT"]), database=db["NAME"],
        query={"charset": "utf8mb4"},
    )


engine = create_engine(database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
