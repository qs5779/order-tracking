"""App routes order level module for fastapi application."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import or_

from app.constants import UNKNOWN
from app.foos import morph_pydantic
from app.models import Order, Piece, Shipper, Vendor
from app.routes.forms.router import router as forms_router
from app.routes.shipper.controller import get_shippers_dict
from app.routes.vendor.controller import get_vendors_dict
from app.schemas.piece import PieceCreate, PieceResponse

Q_USPS = "https://tools.usps.com/go/TrackConfirmAction_input?strOrigTrackNum="


def _get_key_unk(key: Optional[int], isd: dict[int, str]) -> str:
    """Return the value of the key or Unknown.

    Parameters
    ----------
    key : Optional[Union[int,str]]
        The key
    isd : dict[Union[int,str], str]
        The dictionary

    Returns
    -------
    str
        The value or Unknown
    """
    if key:
        return isd.get(key, UNKNOWN)
    return UNKNOWN


def _tracking_link(order: Order, shipper: str) -> str:
    """Return tracking link.

    Parameters
    ----------
    order : Order
        Database order
    shipper : str
        Shipper name

    Returns
    -------
    str
        Tracking link
    """
    if order.trl:
        return order.trl
    if order.trn:
        if shipper == "USPS":
            return "{0}{1}".format(Q_USPS, order.trn)
    return ""


def _oid_url_for(router: APIRouter, oid: int, path: str) -> str:
    """Return a url for path with order_id param.

    Parameters
    ----------
    router : APIRouter
        Router object
    oid : int
        Order identifier
    path : str
        The path for the url

    Returns
    -------
    str
        Short date
    """
    return router.url_path_for(path, order_id=oid)


def _short_date(dt: Optional[datetime]) -> str:
    """Return a short date string.

    Parameters
    ----------
    dt : Optional[datetime]
        Datetime object

    Returns
    -------
    str
        Short date
    """
    if dt:
        return dt.strftime("%m/%d/%Y")
    return ""


def _empty_str(ss: Optional[str]) -> str:
    """Return empty string if ss is None.

    Parameters
    ----------
    ss : Optional[str]
        String to evaluate

    Returns
    -------
    str
        Original string if ss is not None else empty string
    """
    if ss is None:
        return ""
    return ss


def _pieces_url(router: APIRouter, oid: int, db: Session) -> str:
    """Return a url to show pieces for order oid.

    Parameters
    ----------
    router : APIRouter
        The router to use
    oid : int
        The order identifier
    db : Session
        The database session

    Returns
    -------
    str
        The url to show pieces for order oid or empty string if no pieces are found
    """
    pieces_nbr = db.query(func.count(Piece.id)).filter(Piece.order_id == oid).scalar()
    if pieces_nbr > 0:
        return _oid_url_for(router, oid, "items")
    return forms_router.url_path_for("piece_add", order_id=oid)


def get_orders(db: Session, pending: bool = False) -> list[Order]:
    """Return a list of orders.

    Parameters
    ----------
    db : Session
        The database session.
    pending : bool
        When True, only undelivered orders will be returned

    Returns
    -------
    list[Order]
        List of orders.
    """
    if pending:
        return (
            db.query(Order)
            .join(Vendor, Order.vendor_id == Vendor.id)
            .join(Shipper, Order.shipper_id == Shipper.id)
            .filter(or_(Order.delivered == None, func.trim(Order.delivered) == ""))
            .order_by(Order.ordered.desc())
            .all()
        )
    return (
        db.query(Order)
        .join(Vendor, Order.vendor_id == Vendor.id)
        .join(Shipper, Order.shipper_id == Shipper.id)
        .order_by(Order.ordered.desc())
        .all()
    )


def get_orders_dict(  # noqa: WPS210
    router: APIRouter,
    db: Session,
    pending: bool = False,
) -> list[dict[str, str]]:  # noqa: WPS210
    """Return a list of orders in dict form.

    Parameters
    ----------
    router : APIRouter
        The router to use
    db : Session
        The database session.
    pending : bool
        When True, only undelivered orders will be returned

    Returns
    -------
    list[dict[str, str]]
        List of orders in dict form.
    """
    res: list[dict[str, str]] = []
    vd = get_vendors_dict(db)
    sd = get_shippers_dict(db)
    orders = get_orders(db, pending)
    if pending:
        logger.debug("{0} pending orders".format(len(orders)))
    else:
        logger.debug("{0} orders".format(len(orders)))
    for order in orders:
        od: dict[str, str] = {}
        shipper = _get_key_unk(order.shipper_id, sd)
        od["id"] = str(order.id)
        od["oil"] = forms_router.url_path_for("order_get", order_id=order.id)
        od["number"] = order.number
        od["vendor"] = _get_key_unk(order.vendor_id, vd)
        od["ordered"] = _short_date(order.ordered)
        od["shipped"] = _short_date(order.shipped)
        if order.delivered:
            od["delivered"] = _short_date(order.delivered)
        else:
            od["delivered"] = _oid_url_for(router, order.id, "delivered")
        od["arrived"] = _short_date(order.arrived)
        od["created"] = _short_date(order.created)
        od["shipper"] = shipper
        od["trn"] = _empty_str(order.trn)
        od["trl"] = _tracking_link(order, shipper)
        od["notes"] = _empty_str(order.notes)
        od["pieces"] = _pieces_url(router, order.id, db)
        res.append(od)

    # logger.debug("Orders: {0}".format(res))
    return res


def add_pieces(
    oid: int,
    pieces: list[PieceCreate],
    db: Session,
) -> Optional[list[PieceResponse]]:
    """Add pieces to the database.

    Parameters
    ----------
    oid : int
        The order identifier
    pieces : list[PieceCreate]
        List of pieces to add
    db : Session
        Database session

    Returns
    -------
    Optional[list[PieceResponse]]
        List of add item responses
    """
    response: list[PieceResponse] = []
    for piece in pieces:
        record = Piece(order_id=oid, desc=piece.desc, qty=piece.qty)
        db.add(record)
        db.commit()
        db.refresh(record)
        response.append(morph_pydantic(record, PieceResponse))
    if response:
        return response
    return None


def get_pieces(oid: int, db: Session) -> list[Piece]:
    """Return a list of orders.

    Parameters
    ----------
    oid: int
        The order id
    db : Session
        The database session.

    Returns
    -------
    list[Piece]
        List of pieces.
    """
    return db.query(Piece).filter(Piece.order_id == oid).order_by(Piece.id).all()


def get_items_dict(oid: int, db: Session) -> list[dict[str, str]]:
    """Return a list of pieces in dict form.

    Parameters
    ----------
    oid: int
        Order id
    db : Session
        The database session.

    Returns
    -------
    list[dict[str, str]]
        List of pieces in dict form.
    """
    res: list[dict[str, str]] = []
    pieces = get_pieces(oid, db)
    for piece in pieces:
        pd: dict[str, str] = {}
        pd["id"] = str(piece.id)
        pd["pil"] = forms_router.url_path_for("piece_edit", piece_id=piece.id)
        pd["desc"] = piece.desc
        pd["qty"] = str(piece.qty)
        pd["order_id"] = str(piece.order_id)
        res.append(pd)

    logger.debug("Pieces: {0}".format(res))
    return res
