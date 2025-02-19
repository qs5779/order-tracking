"""Routes level module for fastapi application."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.constants import UNKNOWN
from app.foos import OrderTrackingError
from app.models import Order, Piece
from app.routes.shipper.controller import get_shipper_id_by_name
from app.routes.vendor.controller import get_vendor_id_by_name
from app.schemas.order import OrderCreate
from app.schemas.piece import PieceResponse


def _ensure_ordered(record: Order) -> None:
    """Ensure an order has an ordered date."""
    if record.ordered is None:
        if record.shipped is not None:
            record.ordered = record.shipped
        elif record.arrived is not None:
            record.ordered = record.arrived
        elif record.delivered is not None:
            record.ordered = record.delivered
        else:
            record.ordered = datetime.now()


def order_add_or_update(order: OrderCreate, db: Session) -> Order:  # noqa: C901, WPS231
    """Update or insert an order.

    Parameters
    ----------
    order : OrderCreate
        The order create object
    db : Session
        The database connection

    Returns
    -------
    Order
        The resulting record object
    """
    record = (
        db.query(Order).filter(Order.number == order.number).first()
    )  # noqa: WPS221

    # if not, create it
    if record is None:
        record = Order()

    if not order.shipper:
        order.shipper = UNKNOWN
    if not order.vendor:
        order.vendor = UNKNOWN

    # sync the data
    m_data = order.model_dump(exclude_unset=True).items()
    for key, vv in m_data:
        if key == "vendor":
            setattr(record, "vendor_id", get_vendor_id_by_name(vv, db))  # noqa: B010
        elif key == "shipper":
            setattr(record, "shipper_id", get_shipper_id_by_name(vv, db))  # noqa: B010
        elif key == "pieces":
            continue
        else:
            setattr(record, key, vv)

    _ensure_ordered(record)
    # persist the data to the database
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def piece_add_or_update(piece: PieceResponse, db: Session) -> Piece:
    """Update or insert an piece.

    Parameters
    ----------
    piece : PieceResponse
        The piece response object
    db : Session
        The database connection

    Raises
    ------
    OrderTrackingError
        if piece.id and piece.id not in db

    Returns
    -------
    Piece
        The resulting record object
    """
    if piece.id:
        record = db.query(Piece).filter(Piece.id == piece.id).first()  # noqa: WPS221
        if record is None:
            raise OrderTrackingError(
                "Piece id: {0} not found in database".format(piece.id),
            )
        editing = True
    else:
        record = Piece()
        editing = False

    # sync the data
    m_data = piece.model_dump(exclude_unset=True).items()
    for key, vv in m_data:
        if key == "id" and not editing:
            continue
        setattr(record, key, vv)

    # persist the data to the database
    db.add(record)
    db.commit()
    db.refresh(record)

    return record
