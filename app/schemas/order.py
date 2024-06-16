"""Schemas level order module for fastapi application."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from fastapi import Form
from pydantic import BaseModel

# from app.models import Order
from app.schemas.piece import PieceCreate, PieceResponse


@dataclass
class OrderForm:
    """Order from dataclass."""

    number: str = Form(...)
    ordered: str = Form(...)
    shipped: str = Form(...)
    arrived: str = Form(...)
    delivered: str = Form(...)
    notes: str = Form(...)
    trn: str = Form(...)
    trl: str = Form(...)
    vendor: str = Form(...)
    shipper: str = Form(...)


class OrderCreate(BaseModel):
    """Pydantic model order for request data."""

    number: str
    ordered: Optional[datetime] = None
    shipped: Optional[datetime] = None
    arrived: Optional[datetime] = None
    delivered: Optional[datetime] = None
    notes: Optional[str] = None
    trn: Optional[str] = None
    trl: Optional[str] = None
    vendor: Optional[str] = None
    shipper: Optional[str] = None
    pieces: Optional[list[PieceCreate]] = None


class OrderResponse(BaseModel):
    """Pydantic model order for response data."""

    id: int
    number: str
    ordered: Optional[datetime] = None
    shipped: Optional[datetime] = None
    arrived: Optional[datetime] = None
    delivered: Optional[datetime] = None
    notes: Optional[str] = None
    trn: Optional[str] = None
    trl: Optional[str] = None
    created: datetime
    vendor_id: Optional[int] = None
    shipper_id: Optional[int] = None
    pieces: Optional[list[PieceResponse]] = None


# def order_response(order: Order) -> OrderResponse:
#     return OrderResponse(
#         id=order.id,
#         number=order.number,
#         shipped=order.shipped,
#         arrived=order.arrived,
#         delivered=order.delivered,
#         trn=order.trn,
#         trl=order.trl,
#         vendor_id=order.vendor_id,
#         shipper_id=order.shipper_id,
#         created=order.created,
#         notes=order.notes,
#     )
