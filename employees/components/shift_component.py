from datetime import timedelta
from decimal import Decimal

from marshmallow import ValidationError as MarshmallowValidationError
from rest_framework.exceptions import APIException, NotFound, ValidationError

from employees.repositories.shift_repository import ShiftRepository
from employees.sqlalchemy_db import SessionLocal
from employees.models.sqlalchemy_models import ScheduledShiftRecord
from employees.serializers.shift_serializer import (
    AwareDateTimeField,
    EmployeeRateInputSchema,
    ShiftInputSchema,
    as_utc,
)


class Conflict(APIException):
    status_code = 409
    default_detail = "The requested change conflicts with existing data."
    default_code = "conflict"


class ShiftComponent:
    MAX_DURATION = timedelta(hours=24)
    READ_ONLY_FIELDS = {
        "id", "employee", "hourly_rate", "scheduled_hours", "forecasted_pay",
        "business_date", "created_at", "updated_at",
    }

    def __init__(self, repository=None):
        self.repository = repository or ShiftRepository()

    def create_shift(self, employee_id, data):
        with SessionLocal() as session:
            with session.begin():
                employee = self.repository.get_employee(session, employee_id, lock=True)
                if employee is None:
                    raise NotFound()
                values = self._load_shift_input(data, partial=False)
                self._validate_duration(values["start_datetime"], values["end_datetime"])
                self._raise_if_overlap(
                    session,
                    employee_id,
                    values["start_datetime"],
                    values["end_datetime"],
                )
                shift = ScheduledShiftRecord(
                    employee_id=employee_id,
                    start_datetime=values["start_datetime"],
                    end_datetime=values["end_datetime"],
                    hourly_rate=employee.hourly_rate,
                )
                session.add(shift)
                session.flush()
            session.refresh(shift)
            return shift

    def update_shift(self, shift_id, data):
        with SessionLocal() as session:
            with session.begin():
                employee_id = self.repository.get_shift_employee_id(session, shift_id)
                if employee_id is None:
                    raise NotFound()
                if self.repository.get_employee(session, employee_id, lock=True) is None:
                    raise NotFound()
                # Reload under the employee lock so earlier updates cannot leave stale times.
                shift = self.repository.get_shift(session, shift_id, lock=True)
                if shift is None:
                    raise NotFound()
                values = self._load_shift_input(data, partial=True)
                if not values:
                    raise ValidationError({
                        "non_field_errors": ["At least one shift time is required."]
                    })
                start = as_utc(values.get("start_datetime", shift.start_datetime))
                end = as_utc(values.get("end_datetime", shift.end_datetime))
                self._validate_duration(start, end)
                self._raise_if_overlap(session, shift.employee_id, start, end, exclude_id=shift_id)
                shift.start_datetime = start
                shift.end_datetime = end
                session.flush()
            session.refresh(shift)
            return shift

    def delete_shift(self, shift_id):
        with SessionLocal() as session:
            with session.begin():
                shift = self.repository.get_shift(session, shift_id)
                if shift is None:
                    raise NotFound()
                session.delete(shift)

    def get_shift(self, shift_id):
        with SessionLocal() as session:
            shift = self.repository.get_shift(session, shift_id)
            if shift is None:
                raise NotFound()
            session.expunge(shift)
            return shift

    def list_shifts(self, employee_id, start_date=None, end_date=None):
        with SessionLocal() as session:
            if self.repository.get_employee(session, employee_id) is None:
                raise NotFound()
            shifts = self.repository.get_employee_shifts(
                session, employee_id, start_date, end_date
            )
            for shift in shifts:
                session.expunge(shift)
            return shifts

    def forecast_summary(self, employee_id, start_date, end_date):
        shifts = self.list_shifts(employee_id, start_date, end_date)
        hours = sum((shift.scheduled_hours for shift in shifts), Decimal("0.00"))
        pay = sum((shift.forecasted_pay for shift in shifts), Decimal("0.00"))
        return {
            "employee": employee_id,
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
            "shift_count": len(shifts),
            "scheduled_hours": f"{hours:.2f}",
            "forecasted_pay": f"{pay:.2f}",
        }

    def update_employee_rate(self, employee_id, data):
        with SessionLocal() as session:
            with session.begin():
                employee = self.repository.get_employee(session, employee_id, lock=True)
                if employee is None:
                    raise NotFound()
                try:
                    values = EmployeeRateInputSchema().load(data)
                except MarshmallowValidationError as exc:
                    raise ValidationError(exc.messages) from exc
                employee.hourly_rate = values["hourly_rate"]
                session.flush()
            session.refresh(employee)
            return employee.hourly_rate

    @staticmethod
    def _load_shift_input(data, partial):
        readonly_errors = {
            field: ["This field is read-only."]
            for field in ShiftComponent.READ_ONLY_FIELDS
            if field in data
        }
        input_data = {
            key: value for key, value in data.items()
            if key not in ShiftComponent.READ_ONLY_FIELDS
        }
        try:
            values = ShiftInputSchema(partial=partial).load(input_data)
        except MarshmallowValidationError as exc:
            errors = dict(exc.messages)
            errors.update(readonly_errors)
            raise ValidationError(errors) from exc
        if readonly_errors:
            raise ValidationError(readonly_errors)
        return values

    @staticmethod
    def _validate_duration(start, end):
        if end <= start:
            raise ValidationError({"end_datetime": ["End time must be after start time."]})
        if end - start > ShiftComponent.MAX_DURATION:
            raise ValidationError({"end_datetime": ["A shift cannot be longer than 24 hours."]})

    def _raise_if_overlap(self, session, employee_id, start, end, exclude_id=None):
        conflict = self.repository.find_overlap(session, employee_id, start, end, exclude_id)
        if conflict:
            time_field = AwareDateTimeField()
            start_text = time_field._serialize(conflict.start_datetime, None, None)
            end_text = time_field._serialize(conflict.end_datetime, None, None)
            raise ValidationError({
                "non_field_errors": [
                    f"Shift overlaps existing shift {conflict.id} ({start_text} to {end_text})."
                ]
            })
