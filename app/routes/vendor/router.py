"""App routes vendor level module for fastapi application."""

from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.foos import morph_pydantic  # noqa: WPS347
from app.models import Vendor
from app.routes.vendor.controller import get_vendor_by_id, get_vendors
from app.schemas.vendor import VendorCreate, VendorResponse

router = APIRouter(
    prefix="/vendors",
    tags=["Vendors"],
    responses={HTTPStatus.NOT_FOUND: {"description": "Not found"}},
)


@router.get("/", response_description="List of vendors.")
async def list_vendors(db: Session = Depends(get_db)) -> list[VendorResponse]:
    """Return list of vendors."""
    vendors = get_vendors(db)
    return [morph_pydantic(vendor, VendorResponse) for vendor in vendors]


@router.get("/{vendor_id}", response_model=VendorResponse)
async def read_vendor(vendor_id: int, db: Session = Depends(get_db)) -> VendorResponse:
    """Return vendor by ID."""
    vendor = get_vendor_by_id(vendor_id, db)
    return morph_pydantic(vendor, VendorResponse)


@router.post("/add", response_model=VendorResponse)
async def add_vendor(
    vendor: VendorCreate,
    db: Session = Depends(get_db),
) -> VendorResponse:
    """Add a vendor to the database."""
    model = Vendor(name=vendor.name.capitalize())
    db.add(model)
    db.commit()
    db.refresh(model)
    db.close()
    return morph_pydantic(model, VendorResponse)
