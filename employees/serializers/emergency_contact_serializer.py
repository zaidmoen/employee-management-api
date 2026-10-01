import re

from marshmallow import Schema, ValidationError, fields, validate, validates
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from employees.models.sqlalchemy_models import EmergencyContactRecord


class EmergencyContactInputSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(max=100))
    relationship = fields.String(required=True, validate=validate.Length(max=50))
    phone_number = fields.String(required=True, validate=validate.Length(max=25))
    email = fields.Email(required=True, validate=validate.Length(max=254))

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Contact name cannot be blank.")

    @validates("relationship")
    def validate_relationship(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Relationship cannot be blank.")

    @validates("phone_number")
    def validate_phone(self, value, **kwargs):
        if not re.fullmatch(r"[0-9+()\- ]{7,25}", value.strip()):
            raise ValidationError("Enter a valid phone number.")


class EmergencyContactOutputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EmergencyContactRecord
        load_instance = False
        fields = ("id", "name", "relationship", "phone_number", "email", "created_at", "updated_at")

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


EmergencyContactSerializer = EmergencyContactOutputSchema
