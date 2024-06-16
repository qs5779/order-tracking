"""App routes shipper level module for fastapi application."""

from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.foos import morph_pydantic  # noqa: WPS347
from app.models import Shipper
from app.routes.shipper.controller import get_shipper_by_id, get_shippers
from app.schemas.shipper import ShipperCreate, ShipperResponse

router = APIRouter(
    prefix="/shippers",
    tags=["Shippers"],
    responses={HTTPStatus.NOT_FOUND: {"description": "Not found"}},
)


@router.get("/", response_description="List of shippers.")
async def list_shippers(db: Session = Depends(get_db)) -> list[ShipperResponse]:
    """Return list of shippers."""
    shippers = get_shippers(db)
    return [morph_pydantic(shipper, ShipperResponse) for shipper in shippers]


@router.get("/{shipper_id}", response_model=ShipperResponse)
async def read_shipper(
    shipper_id: int,
    db: Session = Depends(get_db),
) -> ShipperResponse:
    """Return shipper by ID."""
    shipper = get_shipper_by_id(shipper_id, db)
    return morph_pydantic(shipper, ShipperResponse)


@router.post("/add", response_model=ShipperResponse)
async def add_shipper(
    shipper: ShipperCreate,
    db: Session = Depends(get_db),
) -> ShipperResponse:
    """Add a shipper to the database."""
    model = Shipper(name=shipper.name.upper())
    db.add(model)
    db.commit()
    db.refresh(model)
    db.close()
    return morph_pydantic(model, ShipperResponse)
