import re
from datetime import date
from decimal import Decimal

from marshmallow import Schema, ValidationError, fields, validate, validates
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from employees.models.sqlalchemy_models import EmployeeRecord


class MoneyInputField(fields.Decimal):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            amount = Decimal(str(value))
        except Exception:
            amount = None
        if amount is not None:
            if amount.as_tuple().exponent < -2:
                raise ValidationError("Ensure that there are no more than 2 decimal places.")
            digits = amount.as_tuple().digits
            total_digits = max(len(digits), len(digits) + amount.as_tuple().exponent)
            if total_digits > 10:
                raise ValidationError("Ensure that there are no more than 10 digits in total.")
        return super()._deserialize(value, attr, data, **kwargs)


class EmployeeInputSchema(Schema):
    first_name = fields.String(required=True, validate=validate.Length(max=80))
    last_name = fields.String(required=True, validate=validate.Length(max=80))
    email = fields.Email(required=True, validate=validate.Length(max=254))
    phone_number = fields.String(load_default="", validate=validate.Length(max=25))
    hire_date = fields.Date(required=True)
    is_active = fields.Boolean(load_default=True)
    department = fields.Integer(required=True, data_key="department")
    hourly_rate = MoneyInputField(load_default=Decimal("0.00"), as_string=True, places=2, validate=validate.Range(min=Decimal("0.00")))

    @validates("first_name")
    def clean_first(self, value, **kwargs):
        return self._clean_name(value, "first_name")

    @validates("last_name")
    def clean_last(self, value, **kwargs):
        return self._clean_name(value, "last_name")

    @validates("email")
    def clean_email(self, value, **kwargs):
        return value.strip().lower()

    @validates("phone_number")
    def clean_phone(self, value, **kwargs):
        value = value.strip()
        if value and not re.fullmatch(r"[0-9+()\- ]{7,25}", value):
            raise ValidationError("Enter a valid phone number.")
        return value

    @validates("hire_date")
    def validate_hire_date(self, value, **kwargs):
        if value > date.today():
            raise ValidationError("Hire date cannot be in the future.")

    @staticmethod
    def _clean_name(value, field):
        value = value.strip()
        if not value:
            raise ValidationError("This field cannot be blank.")
        return value


class EmployeePatchSchema(Schema):
    first_name = fields.String(validate=validate.Length(max=80))
    last_name = fields.String(validate=validate.Length(max=80))
    email = fields.Email(validate=validate.Length(max=254))
    phone_number = fields.String(validate=validate.Length(max=25))
    hire_date = fields.Date()
    is_active = fields.Boolean()
    department = fields.Integer()
    hourly_rate = MoneyInputField(as_string=True, places=2, validate=validate.Range(min=Decimal("0.00")))

    @validates("first_name")
    def validate_first_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("This field cannot be blank.")

    @validates("last_name")
    def validate_last_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("This field cannot be blank.")

    @validates("phone_number")
    def validate_phone_number(self, value, **kwargs):
        if value and not re.fullmatch(r"[0-9+()\- ]{7,25}", value.strip()):
            raise ValidationError("Enter a valid phone number.")

    @validates("hire_date")
    def validate_patch_hire_date(self, value, **kwargs):
        if value > date.today():
            raise ValidationError("Hire date cannot be in the future.")

class EmployeeOutputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EmployeeRecord
        load_instance = False
        fields = ("id", "first_name", "last_name", "full_name", "email", "phone_number", "hire_date", "is_active", "department", "department_name", "hourly_rate", "created_at", "updated_at")

    full_name = fields.String(dump_only=True)
    department = fields.Integer(attribute="department_id", dump_only=True)
    department_name = fields.String(dump_only=True)
    hourly_rate = fields.Decimal(as_string=True, places=2, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class EmployeeTransferSchema(Schema):
    department_id = fields.Integer(required=True)


class NestedEmployeeSchema(EmployeeOutputSchema):
    pass


EmployeeSerializer = EmployeeOutputSchema
EmployeeTransferSerializer = EmployeeTransferSchema
NestedEmployeeSerializer = NestedEmployeeSchema
