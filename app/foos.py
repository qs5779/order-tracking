"""Top level module for fastapi application."""

from typing import Type, TypeVar

from pydantic import BaseModel

from app.models import Base

T = TypeVar("T", bound=BaseModel)  # noqa: WPS111


def morph_pydantic(db_object: Base, pydantic_model: Type[T]) -> T:
    """Convert SQLAlchemy objects to Pydantic models."""
    # do = db_object.__dict__.copy()
    # if "_sa_instance_state" in do:
    #     do.pop("_sa_instance_state")
    return pydantic_model(**db_object.__dict__)
