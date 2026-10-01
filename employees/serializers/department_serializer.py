from marshmallow import Schema, ValidationError, fields, validate, validates
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from employees.models.sqlalchemy_models import DepartmentRecord


class DepartmentInputSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(load_default="")

    @validates("name")
    def clean_name(self, value, **kwargs):
        value = value.strip()
        if len(value) < 2:
            raise ValidationError("Department name must have at least 2 characters.")
        return value


class DepartmentOutputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DepartmentRecord
        load_instance = False
        fields = ("id", "name", "description", "employee_count", "active_employee_count", "created_at", "updated_at")

    employee_count = fields.Integer(dump_only=True)
    active_employee_count = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


DepartmentSerializer = DepartmentOutputSchema
