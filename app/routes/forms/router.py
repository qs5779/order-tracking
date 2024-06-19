"""App routes forms level module for fastapi application."""

from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Optional

from dateutil.parser import parse as parse_date
from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.templating import Jinja2Templates
from loguru import logger
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.config.database import get_db
from app.models import Order, Piece
from app.routes.shared import order_add_or_update, piece_add_or_update
from app.schemas.order import OrderCreate
from app.schemas.piece import PieceResponse

templates = Jinja2Templates(directory="templates/")

router = APIRouter(
    prefix="/forms",
    tags=["Forms"],
    responses={HTTPStatus.NOT_FOUND: {"description": "Not found"}},
)


@router.get("/fetch/{order_id}")
def order_get(
    request: Request,
    order_id: int = 0,
    db: Session = Depends(get_db),
) -> Response:
    """Form for order get route.

    Parameters
    ----------
    request : Request
        Request object
    order_id : int
        The order identifier
    db : Session
        The database session

    Returns
    -------
    Response
        Response object
    """
    if order_id:
        order = db.query(Order).filter(Order.id == order_id).first()
    else:
        order = Order(id=0)
    return templates.TemplateResponse(
        request,
        "order.html.j2",
        context={
            "order": order,
            "action_url": router.url_path_for("order_upsert"),
        },
    )


def _str_to_date(date: Optional[str]) -> Optional[datetime]:
    """Return a datetime object parsed from the date string.

    Parameters
    ----------
    date : Optional[str]
        The string to convert

    Returns
    -------
    Optional[datetime]
        Return datetime if string is converted else None
    """
    if date:
        return parse_date(date)
    return None


@router.post("/upsert")
def order_upsert(  # noqa: WPS211
    number: Annotated[str, Form()],
    oid: Annotated[int, Form()],
    ordered: Optional[str] = Form(None),  # noqa: WPS204
    shipped: Optional[str] = Form(None),
    arrived: Optional[str] = Form(None),
    delivered: Optional[str] = Form(None),
    trn: Optional[str] = Form(None),
    trl: Optional[str] = Form(None),
    vendor: Optional[str] = Form(None),
    shipper: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """Update or add an order from form data.

    Parameters
    ----------
    number : Annotated[str, Form()]
        The order number
    oid : Annotated[int, Form()]
        The order id
    ordered : Optional[str], optional
        The order ordered date, by default Form(None)
    shipped : Optional[str], optional
        The order shipped date, by default Form(None)
    arrived : Optional[str], optional
        The order arrived date, by default Form(None)
    delivered : Optional[str], optional
        The order delivered date, by default Form(None)
    trn : Optional[str], optional
        The order tracking number, by default Form(None)
    trl : Optional[str], optional
        The order hyperlink, by default Form(None)
    vendor : Optional[str], optional
        The order vendor, by default Form(None)
    shipper : Optional[str], optional
        The order shipper, by default Form(None)
    notes : Optional[str], optional
        The order notes, by default Form(None)
    db : Session
        The database session, by default Depends(get_db)

    Returns
    -------
    RedirectResponse
        The OrderResponse object
    """
    order = OrderCreate(
        number=number,
        ordered=_str_to_date(ordered),
        shipped=_str_to_date(shipped),
        arrived=_str_to_date(arrived),
        delivered=_str_to_date(delivered),
        notes=notes,
        trn=trn,
        trl=trl,
        vendor=vendor,
        shipper=shipper,
    )

    record = order_add_or_update(order, db)
    if oid:
        action = "Added"
    else:
        action = "Updated"

    logger.debug("{0} order id: {1}".format(action, record.id))

    return RedirectResponse(
        url="/orders/pending",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/piece_edit/{piece_id}")
def piece_edit(
    request: Request,
    piece_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """Form for piece get route.

    Parameters
    ----------
    request : Request
        Request object
    piece_id : int
        The piece identifier
    db : Session
        The database session

    Raises
    ------
    ValueError
        if piece_id is less than 1

    Returns
    -------
    Response
        Response object
    """
    if piece_id < 1:
        raise ValueError("Invalid piece id: {0}. Must be between >= 1.")

    piece = db.query(Piece).filter(Piece.id == piece_id).first()

    return templates.TemplateResponse(
        request,
        "piece.html.j2",
        context={
            "piece": piece,
            "action_url": router.url_path_for("piece_upsert"),
        },
    )


@router.get("/piece_add/{order_id}")
def piece_add(
    request: Request,
    order_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """Form for piece get route.

    Parameters
    ----------
    request : Request
        Request object
    order_id : int
        The order identifier
    db : Session
        The database session

    Returns
    -------
    Response
        Response object
    """
    piece = Piece(id=0, order_id=order_id)

    return templates.TemplateResponse(
        request,
        "piece.html.j2",
        context={
            "piece": piece,
            "action_url": router.url_path_for("piece_upsert"),
        },
    )


@router.post("/piece_upsert")
def piece_upsert(  # noqa: WPS211
    pid: Annotated[int, Form()],
    desc: Annotated[str, Form()],
    qty: Annotated[int, Form()],
    order_id: Annotated[int, Form()],
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """Update or add a piece from form data.

    Parameters
    ----------
    pid : Annotated[int, Form()]
        The piece id
    desc : Annotated[str, Form()]
        The piece description
    qty : Annotated[int, Form()]
        The piece quantity
    order_id : Annotated[int, Form()]
        The order id
    db : Session
        The database session, by default Depends(get_db)

    Returns
    -------
    RedirectResponse
        The RedirectResponse object
    """
    piece = PieceResponse(id=pid, desc=desc, qty=qty, order_id=order_id)

    record = piece_add_or_update(piece, db)
    if pid:
        action = "Updated"
    else:
        action = "Added"

    logger.debug("{0} order id: {1}".format(action, record.id))

    return RedirectResponse(
        url="/orders/pending",
        status_code=status.HTTP_303_SEE_OTHER,
    )
