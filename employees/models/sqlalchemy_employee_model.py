from decimal import Decimal

from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from .sqlalchemy_base import Base


class EmployeeRecord(Base):
    """SQLAlchemy view of the existing Django employee table."""

    __tablename__ = "employees_employee"

    id: Mapped[int] = mapped_column(primary_key=True)
    hourly_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
