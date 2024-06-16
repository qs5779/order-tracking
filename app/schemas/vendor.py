"""Schemas level vendor module for fastapi application."""

from pydantic import BaseModel


class VendorCreate(BaseModel):
    """Pydantic model vendor for request data."""

    name: str


class VendorResponse(BaseModel):
    """Pydantic model vendor for response data."""

    id: int
    name: str
