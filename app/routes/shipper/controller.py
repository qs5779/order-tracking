"""App routes shipper level module for fastapi application."""

from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Shipper


def get_shipper_by_id(shipper_id: int, db: Session) -> Shipper:
    """Return shipper identified by id.

    Parameters
    ----------
    shipper_id : int
        The shipper id
    db : Session
        The database session.

    Returns
    -------
    Shipper
        The Shipper object

    Raises
    ------
    HTTPException
        HTTPStatus.NOT_FOUND
    """
    shipper = db.query(Shipper).filter(Shipper.id == shipper_id).first()

    # logger.debug("shipper: type: {0}".format(str(type(shipper))))
    if shipper is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="There is no shipper with this id.",
        )

    return shipper


def get_shipper_id_by_name(shipper_nm: str, db: Session) -> int:
    """Return shipper identified by name.

    Parameters
    ----------
    shipper_nm : str
        The shipper name
    db : Session
        The database session.

    Returns
    -------
    int
        The shipper id
    """
    shipper = db.query(Shipper).filter(Shipper.name == shipper_nm).first()

    if shipper is None:
        shipper = Shipper(name=shipper_nm)
        db.add(shipper)
        db.commit()
        db.refresh(shipper)

    return shipper.id


def get_shippers(db: Session) -> list[Shipper]:
    """Return a list of shippers.

    Parameters
    ----------
    db : Session
        The database session.

    Returns
    -------
    list[Shipper]
        List of shippers.
    """
    return db.query(Shipper).all()


def get_shippers_dict(db: Session) -> dict[int, str]:
    """Return a dict of shippers.

    Parameters
    ----------
    db : Session
        The database session.

    Returns
    -------
    dict[int, str]
        Dict of shippers.
    """
    shippers = get_shippers(db)
    sd: dict[int, str] = {}
    for shipper in shippers:
        sd[shipper.id] = shipper.name
    return sd
