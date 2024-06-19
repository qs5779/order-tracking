"""App routes order level module for fastapi application."""

from datetime import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from loguru import logger
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse, Response

from app.config.config import templates
from app.config.database import get_db
from app.constants import VERSION
from app.foos import morph_pydantic  # noqa: WPS347
from app.models import Order
from app.routes.order.controller import (
    add_pieces,
    get_items_dict,
    get_orders_dict,
    get_pieces,
)
from app.routes.shared import order_add_or_update
from app.schemas.order import OrderCreate, OrderResponse
from app.schemas.piece import PieceResponse

# from sqlalchemy import select


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={HTTPStatus.NOT_FOUND: {"description": "Not found"}},
)


@router.get("/delivered/{order_id}")
def delivered(order_id: int, db: Session = Depends(get_db)) -> Response:
    """Redirect to documentation (`/docs/`)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        logger.error("Order id not found: {0}".format(order_id))
    else:
        order.delivered = datetime.now()
        db.add(order)
        db.commit()
    return RedirectResponse(url="/orders/pending")


@router.get("/pieces/{order_id}", response_description="List of pieces.")
async def pieces(order_id: int, db: Session = Depends(get_db)) -> list[PieceResponse]:
    """Return list of pieces."""
    piezas = get_pieces(order_id, db)
    return [morph_pydantic(piece, PieceResponse) for piece in piezas]


@router.get("/items/{order_id}")
async def items(  # noqa: WPS110
    request: Request,
    order_id: int,
    db: Session = Depends(get_db),
) -> HTMLResponse:
    """Return html list of items.

    Parameters
    ----------
    request : Request
        Request object
    order_id : int
        The order identifier
    db : Session
        Session object, by default Depends(get_db)

    Returns
    -------
    HTMLResponse
        The response in html
    """
    context = {
        "pieces": get_items_dict(order_id, db),
        "title": "List of items",
        "rcvd_url": router.url_path_for("delivered", order_id=order_id),
        "pending_url": router.url_path_for("pending"),
        "orders_url": router.url_path_for("orders"),
    }
    return templates.TemplateResponse(request, "items.html.j2", context)


@router.get("/")
async def orders(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    """Return html list of orders.

    Parameters
    ----------
    request : Request
        Request object
    db : Session
        Session object, by default Depends(get_db)

    Returns
    -------
    HTMLResponse
        The response in html
    """
    context = {
        "orders": get_orders_dict(router, db),
        "title": "List of orders",
        "version": VERSION,
        "orders_url": router.url_path_for("pending"),
        "orders_title": "Pending Orders",
    }
    return templates.TemplateResponse(request, "orders.html.j2", context)


@router.get("/pending")
async def pending(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    """Return html list of orders.

    Parameters
    ----------
    request : Request
        Request object
    db : Session
        Session object, by default Depends(get_db)

    Returns
    -------
    HTMLResponse
        The response in html
    """
    undelivered = True
    context = {
        "orders": get_orders_dict(router, db, undelivered),
        "title": "List of pending orders",
        "version": VERSION,
        "orders_url": router.url_path_for("orders"),
        "orders_title": "All Orders",
    }
    return templates.TemplateResponse(request, "orders.html.j2", context)


@router.post("/upsert")
def upsert_order(  # noqa: WPS231, C901
    order: OrderCreate,
    db: Session = Depends(get_db),
) -> OrderResponse:
    """Upsert an order.

    It is used to create a order in the database if it does not already exists,
    else it is used to update the existing one.


    Parameters
    ----------
    order : OrderCreate
        The order create object
    db : Session
        The database connection

    Returns
    -------
    OrderResponse
        The OrderResponse object
    """
    record = order_add_or_update(order, db)
    response = morph_pydantic(record, OrderResponse)
    if order.pieces is not None:
        response.pieces = add_pieces(record.id, order.pieces, db)
    return response
