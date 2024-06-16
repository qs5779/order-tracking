"""Models level order module for fastapi application."""

from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class Order(Base):
    """Orders database class."""

    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(unique=True, index=True)
    ordered: Mapped[Optional[datetime.datetime]]
    shipped: Mapped[Optional[datetime.datetime]]
    arrived: Mapped[Optional[datetime.datetime]]
    delivered: Mapped[Optional[datetime.datetime]]
    notes: Mapped[Optional[str]]
    trn: Mapped[Optional[str]]
    trl: Mapped[Optional[str]]
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    vendor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vendors.id"))
    shipper_id: Mapped[Optional[int]] = mapped_column(ForeignKey("shippers.id"))


class Vendor(Base):
    """Vendor database class."""

    __tablename__ = "vendors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)


class Shipper(Base):
    """Shipper database class."""

    __tablename__ = "shippers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)


class Piece(Base):
    """Piece database class."""

    __tablename__ = "pieces"
    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str]
    qty: Mapped[int] = mapped_column(default=1)

    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orders.id"))


def create_all_tables(engine: Engine) -> None:
    """Create all tables if necessary."""
    Base.metadata.create_all(bind=engine)
