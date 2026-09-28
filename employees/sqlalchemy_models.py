"""Employee data mapped to the existing database tables with SQLAlchemy 2.0."""
from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship as orm_relationship

from .database import Base


class Department(Base):
    __tablename__ = "employees_department"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    employees: Mapped[list["Employee"]] = orm_relationship(back_populates="department")


class Employee(Base):
    __tablename__ = "employees_employee"
    __table_args__ = (
        Index("emp_dept_active_idx", "department_id", "is_active"),
        CheckConstraint("first_name <> ''", name="employee_first_name_not_empty"),
        CheckConstraint("last_name <> ''", name="employee_last_name_not_empty"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    phone_number: Mapped[str] = mapped_column(String(25), default="")
    hire_date: Mapped[date] = mapped_column(Date, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("employees_department.id", ondelete="RESTRICT"))
    # An optional shift keeps old employee rows valid after the migration.
    shift_start: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    shift_end: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    break_minutes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    department: Mapped[Department] = orm_relationship(back_populates="employees")
    emergency_contacts: Mapped[list["EmergencyContact"]] = orm_relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def shift_hours(self):
        if self.shift_start is None or self.shift_end is None:
            return None
        start = self.shift_start.hour * 60 + self.shift_start.minute
        end = self.shift_end.hour * 60 + self.shift_end.minute
        minutes = (end - start) % 1440
        # Equal times mean a 24-hour shift, not a zero-hour shift.
        if minutes == 0:
            minutes = 1440
        return round((minutes - self.break_minutes) / 60, 2)


class EmergencyContact(Base):
    __tablename__ = "employees_emergencycontact"
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees_employee.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    relationship: Mapped[str] = mapped_column(String(50))
    phone_number: Mapped[str] = mapped_column(String(25))
    email: Mapped[str] = mapped_column(String(254))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    employee: Mapped[Employee] = orm_relationship(back_populates="emergency_contacts")
