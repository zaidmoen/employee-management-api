from datetime import datetime, timezone as dt_timezone
from decimal import Decimal

from marshmallow import Schema, ValidationError, fields, validate, validates_schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from employees.sqlalchemy_models import ScheduledShiftRecord


def as_utc(value):
    """MySQL DATETIME values are naive, but this project stores them as UTC."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=dt_timezone.utc)
    return value.astimezone(dt_timezone.utc)


class AwareDateTimeField(fields.Field):
    default_error_messages = {
        "invalid": "Not a valid ISO 8601 datetime.",
        "offset": "Datetime must include a timezone offset, e.g. 2026-10-01T09:00:00Z.",
        "minute": "Time must be a whole minute (seconds must be 0).",
    }

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, str):
            raise self.make_error("invalid")
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise self.make_error("invalid") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise self.make_error("offset")
        if parsed.second or parsed.microsecond:
            raise self.make_error("minute")
        return as_utc(parsed)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return as_utc(value).isoformat(timespec="seconds").replace("+00:00", "Z")


class StrictMoneyInputField(fields.Decimal):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            raw_value = Decimal(str(value))
        except Exception:
            raw_value = None
        if raw_value is not None and raw_value.as_tuple().exponent < -2:
            raise ValidationError(
                "Ensure that there are no more than 2 decimal places."
            )
        if raw_value is not None:
            digits = raw_value.as_tuple().digits
            total_digits = max(
                len(digits),
                len(digits) + raw_value.as_tuple().exponent,
            )
            if total_digits > 10:
                raise ValidationError("Ensure that there are no more than 10 digits in total.")
        result = super()._deserialize(value, attr, data, **kwargs)
        return result


class ShiftInputSchema(Schema):
    start_datetime = AwareDateTimeField()
    end_datetime = AwareDateTimeField()


class ShiftOutputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ScheduledShiftRecord
        include_fk = True
        load_instance = False
        fields = (
            "id", "employee", "start_datetime", "end_datetime", "business_date",
            "hourly_rate", "scheduled_hours", "forecasted_pay", "created_at",
            "updated_at",
        )

    id = fields.Integer(dump_only=True)
    employee = fields.Integer(attribute="employee_id", dump_only=True)
    start_datetime = AwareDateTimeField(dump_only=True)
    end_datetime = AwareDateTimeField(dump_only=True)
    business_date = fields.Method("get_business_date", dump_only=True)
    hourly_rate = fields.Decimal(as_string=True, places=2, dump_only=True)
    scheduled_hours = fields.Method("get_scheduled_hours", dump_only=True)
    forecasted_pay = fields.Method("get_forecasted_pay", dump_only=True)
    created_at = AwareDateTimeField(dump_only=True)
    updated_at = AwareDateTimeField(dump_only=True)

    @staticmethod
    def get_business_date(shift):
        return shift.business_date.isoformat()

    @staticmethod
    def get_scheduled_hours(shift):
        return f"{shift.scheduled_hours:.2f}"

    @staticmethod
    def get_forecasted_pay(shift):
        return f"{shift.forecasted_pay:.2f}"


class ShiftListQuerySchema(Schema):
    class Meta:
        unknown = "exclude"

    from_date = fields.Date(
        data_key="from",
        load_default=None,
        error_messages={"invalid": "Date has wrong format. Use YYYY-MM-DD."},
    )
    to_date = fields.Date(
        data_key="to",
        load_default=None,
        error_messages={"invalid": "Date has wrong format. Use YYYY-MM-DD."},
    )

    @validates_schema
    def validate_range(self, values, **kwargs):
        start = values.get("from_date")
        end = values.get("to_date")
        if start and end and start > end:
            raise ValidationError({"non_field_errors": ["from must be on or before to."]})
        return values


class ForecastQuerySchema(Schema):
    from_date = fields.Date(
        data_key="from",
        required=True,
        error_messages={"invalid": "Date has wrong format. Use YYYY-MM-DD."},
    )
    to_date = fields.Date(
        data_key="to",
        required=True,
        error_messages={"invalid": "Date has wrong format. Use YYYY-MM-DD."},
    )

    @validates_schema
    def validate_range(self, values, **kwargs):
        if values["from_date"] > values["to_date"]:
            raise ValidationError(
                {"non_field_errors": ["from must be on or before to."]}
            )


class EmployeeRateInputSchema(Schema):
    hourly_rate = StrictMoneyInputField(
        required=True,
        as_string=True,
        places=2,
        validate=validate.Range(min=Decimal("0.00")),
        error_messages={"invalid": "A valid number is required."},
    )


