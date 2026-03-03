"""Config level module for fastapi application."""

import os
from typing import Any, Generator

from loguru import logger
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config.config import cfg

# Database setup
# DATABASE_URL = "sqlite:///./test.db"

if not os.path.exists("/tmp/database_url.txt"):
    with open("/tmp/database_url.txt", "w") as ff:
        ff.write("{0}\n".format(cfg.database_url))
        ff.write("{0}\n".format(cfg.env_state))


engine = create_engine(cfg.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# declarative base class
class Base(DeclarativeBase):
    """Declarative base class."""


# Base = sqlalchemy.orm.declarative_base()


def get_db() -> Generator[Session, Any, Any]:
    """Return a database session."""
    db = SessionLocal()
    try:  # noqa: WPS501
        yield db
    except exc.SQLAlchemyError as ex:
        logger.exception(str(ex))
    finally:
        db.close()
