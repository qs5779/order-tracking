"""Schemas level shipper module for fastapi application."""

from pydantic import BaseModel


class ShipperCreate(BaseModel):
    """Pydantic model shipper for request data."""

    name: str


class ShipperResponse(BaseModel):
    """Pydantic model shipper for response data."""

    id: int
    name: str
