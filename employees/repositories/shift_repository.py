from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from django.conf import settings
from sqlalchemy import select

from employees.models.sqlalchemy_employee_model import EmployeeRecord
from employees.models.sqlalchemy_shift_model import ScheduledShiftRecord


class ShiftRepository:
    def get_employee(self, session, employee_id, lock=False):
        statement = select(EmployeeRecord).where(EmployeeRecord.id == employee_id)
        if lock:
            statement = statement.with_for_update()
        return session.scalar(statement)

    def get_shift(self, session, shift_id, lock=False):
        statement = select(ScheduledShiftRecord).where(
            ScheduledShiftRecord.id == shift_id
        )
        if lock:
            statement = statement.with_for_update()
        return session.scalar(statement)

    def get_shift_employee_id(self, session, shift_id):
        statement = select(ScheduledShiftRecord.employee_id).where(
            ScheduledShiftRecord.id == shift_id
        )
        return session.scalar(statement)

    def find_overlap(self, session, employee_id, start, end, exclude_id=None):
        statement = select(ScheduledShiftRecord).where(
            ScheduledShiftRecord.employee_id == employee_id,
            ScheduledShiftRecord.start_datetime < end,
            ScheduledShiftRecord.end_datetime > start,
        )
        if exclude_id is not None:
            statement = statement.where(ScheduledShiftRecord.id != exclude_id)
        # A locking read sees rows committed while this transaction waited on the employee.
        statement = statement.with_for_update()
        return session.scalar(statement.order_by(ScheduledShiftRecord.start_datetime))

    def get_employee_shifts(self, session, employee_id, start_date=None, end_date=None):
        statement = select(ScheduledShiftRecord).where(
            ScheduledShiftRecord.employee_id == employee_id
        )
        if start_date:
            start = datetime.combine(start_date, time.min, tzinfo=ZoneInfo(settings.TIME_ZONE))
            statement = statement.where(
                ScheduledShiftRecord.start_datetime >= start.astimezone(timezone.utc)
            )
        if end_date:
            next_day = end_date + timedelta(days=1)
            end = datetime.combine(next_day, time.min, tzinfo=ZoneInfo(settings.TIME_ZONE))
            statement = statement.where(
                ScheduledShiftRecord.start_datetime < end.astimezone(timezone.utc)
            )
        return list(session.scalars(statement.order_by(ScheduledShiftRecord.start_datetime)))

    def get_shift_summary(self, session, employee_id, start_date, end_date):
        return self.get_employee_shifts(session, employee_id, start_date, end_date)
