"""App routes vendor level module for fastapi application."""

from http import HTTPStatus

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.orm import Session

from app.models import Vendor


def get_vendor_by_id(vendor_id: int, db: Session) -> Vendor:
    """Return vendor identified by id.

    Parameters
    ----------
    vendor_id : int
        The vendor id
    db : Session
        The database session.

    Returns
    -------
    Vendor
        The Vendor object

    Raises
    ------
    HTTPException
        HTTPStatus.NOT_FOUND
    """
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()

    logger.debug("vendor: type: {0}".format(str(type(vendor))))
    if vendor is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="There is no vendor with this id.",
        )

    return vendor


def get_vendor_id_by_name(vendor_nm: str, db: Session) -> int:
    """Return vendor identified by name.

    Parameters
    ----------
    vendor_nm : str
        The vendor name
    db : Session
        The database session.

    Returns
    -------
    int
        The Vendor id
    """
    vendor = db.query(Vendor).filter(Vendor.name == vendor_nm).first()

    if vendor is None:
        vendor = Vendor(name=vendor_nm)
        db.add(vendor)
        db.commit()
        db.refresh(vendor)

    return vendor.id


def get_vendors(db: Session) -> list[Vendor]:
    """Return a list of vendors.

    Parameters
    ----------
    db : Session
        The database session.

    Returns
    -------
    list[Vendor]
        List of vendors.
    """
    res = db.query(Vendor).all()
    logger.debug("res: type: {0}".format(str(type(res))))
    return res


def get_vendors_dict(db: Session) -> dict[int, str]:
    """Return a dict of vendors.

    Parameters
    ----------
    db : Session
        The database session.

    Returns
    -------
    dict[int, str]
        Dict of vendors.
    """
    vendors = get_vendors(db)
    sd: dict[int, str] = {}
    for vendor in vendors:
        sd[vendor.id] = vendor.name
    return sd
