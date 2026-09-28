"""Marshmallow handles input validation and SQLAlchemy object output."""
import re
from datetime import date

from marshmallow import Schema, ValidationError, fields, validates_schema, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from employees.sqlalchemy_models import Department, Employee, EmergencyContact


class DepartmentSchema(SQLAlchemyAutoSchema):
    employee_count = fields.Integer(dump_only=True)
    active_employee_count = fields.Integer(dump_only=True)

    class Meta:
        model = Department
        load_instance = False
        include_fk = True
        exclude = ("employees",)


class EmployeeSchema(SQLAlchemyAutoSchema):
    department = fields.Integer(attribute="department_id")
    department_name = fields.String(attribute="department.name", dump_only=True)
    full_name = fields.String(dump_only=True)
    shift_hours = fields.Float(dump_only=True, allow_none=True)

    class Meta:
        model = Employee
        load_instance = False
        exclude = ("department_id", "emergency_contacts")


class ContactSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EmergencyContact
        load_instance = False
        exclude = ("employee", "employee_id")


def cleaned(value):
    value = value.strip()
    if not value:
        raise ValidationError("This field cannot be blank.")
    return value


def phone(value):
    value = value.strip()
    if value and not re.fullmatch(r"[0-9+()\- ]{7,25}", value):
        raise ValidationError("Enter a valid phone number.")
    return value


def email(value):
    return fields.Email().deserialize(value.strip().lower())


class DepartmentInput(Schema):
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    description = fields.String(load_default="")

    @validates_schema
    def strip_name(self, data, **kwargs):
        if "name" in data:
            data["name"] = cleaned(data["name"])


class EmployeeInput(Schema):
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    email = fields.Function(deserialize=email, required=True)
    phone_number = fields.Function(deserialize=phone, load_default="")
    hire_date = fields.Date(required=True)
    is_active = fields.Boolean(load_default=True)
    department = fields.Integer(required=True)
    shift_start = fields.Time(allow_none=True, load_default=None)
    shift_end = fields.Time(allow_none=True, load_default=None)
    break_minutes = fields.Integer(load_default=0, validate=validate.Range(min=0))

    @validates_schema
    def check_values(self, data, **kwargs):
        errors = {}
        for name in ("first_name", "last_name"):
            if name in data:
                try:
                    data[name] = cleaned(data[name])
                except ValidationError as exc:
                    errors[name] = exc.messages
        if data.get("hire_date", date.min) > date.today():
            errors["hire_date"] = ["Hire date cannot be in the future."]
        if errors:
            raise ValidationError(errors)


class ContactInput(Schema):
    name = fields.String(required=True)
    relationship = fields.String(required=True)
    phone_number = fields.Function(deserialize=phone, required=True)
    email = fields.Function(deserialize=email, required=True)

    @validates_schema
    def check_names(self, data, **kwargs):
        errors = {}
        for name in ("name", "relationship"):
            if name in data:
                try:
                    data[name] = cleaned(data[name])
                except ValidationError as exc:
                    errors[name] = exc.messages
        if errors:
            raise ValidationError(errors)
