from datetime import datetime, timezone

from rest_framework.exceptions import NotFound, ValidationError
from sqlalchemy.exc import IntegrityError

from employees.components.validation import load_schema
from employees.models.sqlalchemy_models import EmployeeRecord
from employees.repositories import EmergencyContactRepository
from employees.serializers.emergency_contact_serializer import EmergencyContactInputSchema
from employees.sqlalchemy_db import SessionLocal


class EmergencyContactComponent:
    def __init__(self, repository=None):
        self.repository = repository or EmergencyContactRepository()

    def get_contacts_for_employee(self, employee_id):
        with SessionLocal() as session:
            if session.get(EmployeeRecord, employee_id) is None:
                raise NotFound({"employee": "Employee does not exist."})
            records = self.repository.get_for_employee(session, employee_id)
            for record in records:
                session.expunge(record)
            return records

    def get_contact(self, employee_id, contact_id):
        with SessionLocal() as session:
            if session.get(EmployeeRecord, employee_id) is None:
                raise NotFound({"employee": "Employee does not exist."})
            contact = self.repository.get_by_id(session, contact_id)
            if contact is None or contact.employee_id != employee_id:
                raise NotFound("The requested resource does not exist under this employee.")
            session.expunge(contact)
            return contact

    def create_contact(self, employee_id, data):
        values = load_schema(EmergencyContactInputSchema(), data)
        values = self._clean(values)
        with SessionLocal() as session:
            with session.begin():
                if session.get(EmployeeRecord, employee_id) is None:
                    raise NotFound({"employee": "Employee does not exist."})
                contact = self.repository.create_for_employee(session, employee_id, values)
            session.expunge(contact)
            return contact

    def update_contact(self, employee_id, contact_id, data, partial=True):
        values = load_schema(EmergencyContactInputSchema(partial=partial), data)
        values = self._clean(values)
        if not partial:
            required = {"name", "relationship", "phone_number", "email"}
            missing = {key: ["Missing data for required field."] for key in required if key not in values}
            if missing:
                raise ValidationError(missing)
        with SessionLocal() as session:
            with session.begin():
                contact = self.repository.get_by_id(session, contact_id)
                if contact is None or contact.employee_id != employee_id:
                    raise NotFound("The requested resource does not exist under this employee.")
                for key, value in values.items():
                    setattr(contact, key, value)
                contact.updated_at = datetime.now(timezone.utc)
            session.expunge(contact)
            return contact

    def delete_contact(self, employee_id, contact_id):
        with SessionLocal() as session:
            with session.begin():
                contact = self.repository.get_by_id(session, contact_id)
                if contact is None or contact.employee_id != employee_id:
                    raise NotFound("The requested resource does not exist under this employee.")
                session.delete(contact)

    @staticmethod
    def _clean(values):
        if "name" in values:
            values["name"] = values["name"].strip()
            if not values["name"]:
                raise ValidationError({"name": "Contact name cannot be blank."})
        if "relationship" in values:
            values["relationship"] = values["relationship"].strip()
            if not values["relationship"]:
                raise ValidationError({"relationship": "Relationship cannot be blank."})
        if "phone_number" in values:
            values["phone_number"] = values["phone_number"].strip()
        if "email" in values:
            values["email"] = values["email"].strip().lower()
        return values
