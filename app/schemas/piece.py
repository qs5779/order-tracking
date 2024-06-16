"""Schemas level piece module for fastapi application."""

from pydantic import BaseModel


class PieceCreate(BaseModel):
    """Pydantic model piece for request data."""

    desc: str
    qty: int = 1


class PieceResponse(BaseModel):
    """Pydantic model piece for response data."""

    id: int
    desc: str
    qty: int
    order_id: int
