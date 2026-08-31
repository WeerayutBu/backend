"""SQLAlchemy base model used by persistence adapters."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
