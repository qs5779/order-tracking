"""Routes level module for fastapi application."""

from sqlalchemy.orm import Session

from app.constants import UNKNOWN
from app.models import Order
from app.routes.shipper.controller import get_shipper_id_by_name
from app.routes.vendor.controller import get_vendor_id_by_name
from app.schemas.order import OrderCreate


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

    # persist the data to the database
    db.add(record)
    db.commit()
    db.refresh(record)

    return record
