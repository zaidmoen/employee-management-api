"""SQLAlchemy mappings for the tables managed by the existing Django migrations.

The Django model classes stay as migration/admin compatibility declarations. All
application reads and writes go through these SQLAlchemy records.
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

from django.conf import settings
from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index
from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DepartmentRecord(Base):
    __tablename__ = "employees_department"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class EmployeeRecord(Base):
    __tablename__ = "employees_employee"
    __table_args__ = (
        Index("emp_dept_active_idx", "department_id", "is_active"),
        CheckConstraint("first_name != ''", name="employee_first_name_not_empty"),
        CheckConstraint("last_name != ''", name="employee_last_name_not_empty"),
        CheckConstraint("hourly_rate >= 0", name="employee_hourly_rate_non_negative"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80), nullable=False)
    last_name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(25), nullable=False, default="")
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    department_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("employees_department.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class EmergencyContactRecord(Base):
    __tablename__ = "employees_emergencycontact"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("employees_employee.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    relationship: Mapped[str] = mapped_column(String(50), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(25), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ScheduledShiftRecord(Base):
    __tablename__ = "employees_scheduledshift"
    __table_args__ = (
        CheckConstraint("end_datetime > start_datetime", name="shift_end_after_start"),
        Index("shift_employee_start_idx", "employee_id", "start_datetime"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    employee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("employees_employee.id", ondelete="RESTRICT"), nullable=False)
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def scheduled_hours(self):
        duration = self.end_datetime - self.start_datetime
        minutes = Decimal(duration.days * 1440 + duration.seconds // 60)
        return (minutes / Decimal("60")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def forecasted_pay(self):
        duration = self.end_datetime - self.start_datetime
        minutes = Decimal(duration.days * 1440 + duration.seconds // 60)
        return ((minutes / Decimal("60")) * self.hourly_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def business_date(self):
        value = self.start_datetime
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(ZoneInfo(settings.TIME_ZONE)).date()
