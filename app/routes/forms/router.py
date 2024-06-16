"""App routes forms level module for fastapi application."""

from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Optional

from dateutil.parser import parse as parse_date
from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.templating import Jinja2Templates
from loguru import logger
from num2words import num2words as spell_number
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.config.database import get_db
from app.models import Order
from app.routes.order.controller import order_add_or_update
from app.schemas.order import OrderCreate

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
        order = Order()
    return templates.TemplateResponse(
        "order.html.j2",
        context={
            "request": request,
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


@router.get("/test")
def form_get(request: Request) -> Response:
    """Form get route.

    Parameters
    ----------
    request : Request
        Request object

    Returns
    -------
    Response
        Response object
    """
    res = "Type a number"
    return templates.TemplateResponse(
        "form.html",
        context={"request": request, "result": res},
    )


@router.post("/test")
def form_post(request: Request, num: int = Form(...)) -> Response:
    """Form get route.

    Parameters
    ----------
    request : Request
        Request object
    num: int
        Form data

    Returns
    -------
    Response
        Response object
    """
    res = spell_number(num)
    return templates.TemplateResponse(
        "form.html",
        context={"request": request, "result": res},
    )
