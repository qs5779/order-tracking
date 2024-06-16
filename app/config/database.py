"""Config level module for fastapi application."""

from typing import Any, Generator

from loguru import logger
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config.config import cfg

# Database setup
# DATABASE_URL = "sqlite:///./test.db"
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
