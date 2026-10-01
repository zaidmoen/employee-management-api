from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from django.conf import settings


class Base(DeclarativeBase):
    pass


class EmployeeRecord(Base):
    """SQLAlchemy view of the existing Django employee table."""

    __tablename__ = "employees_employee"

    id: Mapped[int] = mapped_column(primary_key=True)
    hourly_rate: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )


class ScheduledShiftRecord(Base):
    __tablename__ = "employees_scheduledshift"
    __table_args__ = (
        CheckConstraint(
            "end_datetime > start_datetime",
            name="shift_end_after_start",
        ),
        Index("shift_employee_start_idx", "employee_id", "start_datetime"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees_employee.id", ondelete="RESTRICT"),
        nullable=False,
    )
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def scheduled_hours(self):
        duration = self.end_datetime - self.start_datetime
        minutes = Decimal(duration.days * 1440 + duration.seconds // 60)
        return (minutes / Decimal("60")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    @property
    def forecasted_pay(self):
        duration = self.end_datetime - self.start_datetime
        minutes = Decimal(duration.days * 1440 + duration.seconds // 60)
        exact_pay = (minutes / Decimal("60")) * self.hourly_rate
        return exact_pay.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def business_date(self):
        from zoneinfo import ZoneInfo

        value = self.start_datetime
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(ZoneInfo(settings.TIME_ZONE)).date()
